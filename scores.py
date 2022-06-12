#scores.py by x0rnn, shows player/team info such as kills, deaths, damage given, damage received, elos, average team elo, etc. See: http://imgur.com/a/s2suj

import minqlx
import requests
import itertools
import threading
import time
from operator import itemgetter

MAX_ATTEMPTS = 3
CACHE_EXPIRE = 60*30 # 30 minutes TTL.
DEFAULT_RATING = 1500
SUPPORTED_GAMETYPES = ("ca", "ctf", "dom", "ft", "tdm")
# Externally supported game types. Used by !getrating for game types the API works with.
EXT_SUPPORTED_GAMETYPES = ("ca", "ctf", "dom", "ft", "tdm", "duel", "ffa")

class scores(minqlx.Plugin):
    def __init__(self):
        self.add_command("scores", self.cmd_scores)

        self.ratings_lock = threading.RLock()
        # Keys: steam_id - Items: {"ffa": {"elo": 123, "games": 321, "local": False}, ...}
        self.ratings = {}
        # Keys: request_id - Items: (players, callback)
        self.requests = {}
        self.request_counter = itertools.count()

        self.api_url = "http://{}/{}/".format(self.get_cvar("qlx_balanceUrl"), self.get_cvar("qlx_balanceApi"))

    @minqlx.thread
    def fetch_ratings(self, player, players, request_id):
        # We don't want to modify the actual dict, so we use a copy.
        players = players.copy()

        attempts = 0
        last_status = 0
        while attempts < MAX_ATTEMPTS:
            attempts += 1
            url = self.api_url + "+".join([str(sid) for sid in players])
            res = requests.get(url)
            last_status = res.status_code
            if res.status_code != requests.codes.ok:
                continue
            
            js = res.json()
            if "players" not in js:
                last_status = -1
                continue

            # Fill our ratings dict with the ratings we just got.
            for p in js["players"]:
                sid = int(p["steamid"])
                del p["steamid"]
                t = time.time()

                with self.ratings_lock:
                    if sid not in self.ratings:
                        self.ratings[sid] = {}
                    
                    for gt in p:
                        p[gt]["time"] = t
                        p[gt]["local"] = False
                        self.ratings[sid][gt] = p[gt]
                        if self.ratings[sid][gt]["elo"] == 0 and self.ratings[sid][gt]["games"] == 0:
                            self.ratings[sid][gt]["elo"] = DEFAULT_RATING
                        
                        if sid in players and gt == players[sid]:
                            # The API gave us the game type we wanted, so we remove it.
                            del players[sid]

                    # Fill the rest of the game types the API didn't return but supports.
                    for gt in SUPPORTED_GAMETYPES:
                        if gt not in self.ratings[sid]:
                            self.ratings[sid][gt] = {"games": -1, "elo": DEFAULT_RATING, "local": False, "time": time.time()}

            # If the API didn't return all the players, we set them to the default rating.
            for sid in players:
                with self.ratings_lock:
                    if sid not in self.ratings:
                        self.ratings[sid] = {}
                    self.ratings[sid][players[sid]] = {"games": -1, "elo": DEFAULT_RATING, "local": False, "time": time.time()}

            break

        if attempts == MAX_ATTEMPTS:
            self.handle_ratings_fetched(player, request_id, last_status)
            return

        self.handle_ratings_fetched(player, request_id, requests.codes.ok)

    @minqlx.next_frame
    def handle_ratings_fetched(self, player, request_id, status_code):
        players, callback, args = self.requests[request_id]
        del self.requests[request_id]
        if status_code != requests.codes.ok:
            # TODO: Put a couple of known errors here for more detailed feedback.
            player.tell("ERROR {}: Failed to fetch ratings.".format(status_code))
        else:
            callback(player, players, *args)

    def add_request(self, player, players, callback, *args):
        req = next(self.request_counter)
        self.requests[req] = players.copy(), callback, args

        # Only start a new thread if we need to make an API request.
        if self.remove_cached(players):
            self.fetch_ratings(player, players, req)
        else:
            # All players were cached, so we tell it to go ahead and call the callbacks.
            self.handle_ratings_fetched(player, req, requests.codes.ok)

    def remove_cached(self, players):
        with self.ratings_lock:
            for sid in players.copy():
                gt = players[sid]
                if sid in self.ratings and gt in self.ratings[sid]:
                    t = self.ratings[sid][gt]["time"]
                    if t == -1 or time.time() < t + CACHE_EXPIRE:
                        del players[sid]

        return players

    def cmd_scores(self, player, msg, channel):
        gt = self.game.type_short
        if gt not in EXT_SUPPORTED_GAMETYPES:
            player.tell("Cannot get Elo ratings for this gametype.")
            return minqlx.RET_STOP_ALL
        
        if gt == "ffa" or gt == "duel":
            players = dict([(p.steam_id, gt) for p in self.teams()["free"]])
        else:
            players = dict([(p.steam_id, gt) for p in self.teams()["red"] + self.teams()["blue"]])
        self.add_request(player, players, self.callback_ratings)

    def callback_ratings(self, player, players):
        teams = self.teams()
        gt = self.game.type_short

        if self.game.type_short == "ffa" or self.game.type_short == "duel":
            players = []
            for pl in self.teams()["free"]:
                players.append(dict(name=pl.clean_name, score=pl.stats.score, kills=pl.stats.kills, deaths=pl.stats.deaths, dg=pl.stats.damage_dealt, dr=pl.stats.damage_taken, elo=self.ratings[pl.steam_id][gt]["elo"], time=int(pl.stats.time / 60000)))
            output = ["{:^31} | {:^6} | {:^4} | {:^4} | {:^6} | {:^6} | {:^6} | {}".format("Name", "Scr", "Kll", "Dth", "DG", "DR", "Elo", "Time")]
            for p in sorted(players, key=itemgetter("score"), reverse=True):
                output.append("{name:^31} | {score:^6} | {kills:^4} | {deaths:^4} | {dg:^6} | {dr:^6} | {elo:^6} | {time}min".format(**p))
            for count, line in enumerate(output, start=1):
                player.tell(line)
        else:
            red_players = []
            red_kills = 0
            red_deaths = 0
            red_dg = 0
            red_dr = 0
            red_elo = 0
            blue_players = []
            blue_kills = 0
            blue_deaths = 0
            blue_dg = 0
            blue_dr = 0
            blue_elo = 0

            for pl in self.teams()["red"]:
                red_players.append(dict(name=pl.clean_name, score=pl.stats.score, kills=pl.stats.kills, deaths=pl.stats.deaths, dg=pl.stats.damage_dealt, dr=pl.stats.damage_taken, elo=self.ratings[pl.steam_id][gt]["elo"], time=int(pl.stats.time / 60000)))
                red_kills += pl.stats.kills
                red_deaths += pl.stats.deaths
                red_dg += pl.stats.damage_dealt
                red_dr += pl.stats.damage_taken
                red_elo += self.ratings[pl.steam_id][gt]["elo"]

            for pl in self.teams()["blue"]:
                blue_players.append(dict(name=pl.clean_name, score=pl.stats.score, kills=pl.stats.kills, deaths=pl.stats.deaths, dg=pl.stats.damage_dealt, dr=pl.stats.damage_taken, elo=self.ratings[pl.steam_id][gt]["elo"], time=int(pl.stats.time / 60000)))
                blue_kills += pl.stats.kills
                blue_deaths += pl.stats.deaths
                blue_dg += pl.stats.damage_dealt
                blue_dr += pl.stats.damage_taken
                blue_elo += self.ratings[pl.steam_id][gt]["elo"]

            if not len(teams["red"]) == 0:
                avg_red_elo = int(red_elo / len(teams["red"]))
            else:
                avg_red_elo = 0
            if not len(teams["blue"]) == 0:
                avg_blue_elo = int(blue_elo / len(teams["blue"]))
            else:
                avg_blue_elo = 0
            red_output = ["{:^31} | {:^6} | {:^4} | {:^4} | {:^6} | {:^6} | {:^6} | {}".format("Name", "Scr", "Kll", "Dth", "DG", "DR", "Elo", "Time")]
            blue_output = ["{:^31} | {:^6} | {:^4} | {:^4} | {:^6} | {:^6} | {:^6} | {}".format("Name", "Scr", "Kll", "Dth", "DG", "DR", "Elo", "Time")]

            for p in sorted(red_players, key=itemgetter("score"), reverse=True):
                red_output.append("{name:^31} | {score:^6} | {kills:^4} | {deaths:^4} | {dg:^6} | {dr:^6} | {elo:^6} | {time}min".format(**p))
            for p in sorted(blue_players, key=itemgetter("score"), reverse=True):
                blue_output.append("{name:^31} | {score:^6} | {kills:^4} | {deaths:^4} | {dg:^6} | {dr:^6} | {elo:^6} | {time}min".format(**p))

            if self.game.red_score > self.game.blue_score:
                player.tell("^1Red team:")
                for count, line in enumerate(red_output, start=1):
                    player.tell(line)
                player.tell("^5{:^31} ^7| {:^6} | {:^4} | {:^4} | {:^6} | {:^6} | {:^6} |".format("Totals", self.game.red_score, red_kills, red_deaths, red_dg, red_dr, avg_red_elo))
                player.tell("^3---------------------------------------------------------------------------------------")
                player.tell("^4Blue team:")
                for count, line in enumerate(blue_output, start=1):
                    player.tell(line)
                player.tell("^5{:^31} ^7| {:^6} | {:^4} | {:^4} | {:^6} | {:^6} | {:^6} |".format("Totals", self.game.blue_score, blue_kills, blue_deaths, blue_dg, blue_dr, avg_blue_elo))
            else:
                player.tell("^4Blue team:")
                for count, line in enumerate(blue_output, start=1):
                    player.tell(line)
                player.tell("^5{:^31} ^7| {:^6} | {:^4} | {:^4} | {:^6} | {:^6} | {:^6} |".format("Totals", self.game.blue_score, blue_kills, blue_deaths, blue_dg, blue_dr, avg_blue_elo))
                player.tell("^3---------------------------------------------------------------------------------------")
                player.tell("^1Red team:")
                for count, line in enumerate(red_output, start=1):
                    player.tell(line)
                player.tell("^5{:^31} ^7| {:^6} | {:^4} | {:^4} | {:^6} | {:^6} | {:^6} |".format("Totals", self.game.red_score, red_kills, red_deaths, red_dg, red_dr, avg_red_elo))
