#scores.py by x0rnn, shows player/team info such as kills, deaths, damage given, damage received, etc. See: http://imgur.com/a/o2E1i

import minqlx
from operator import itemgetter

class scores(minqlx.Plugin):
    def __init__(self):
        self.add_command("scores", self.cmd_scores)
        self.free_check = False

    def cmd_scores(self, player, msg, channel):
        if self.get_cvar("g_gametype") == "0" or self.get_cvar("g_gametype") == "1":
            self.free_check = True
        else:
            self.free_check = False

        if self.free_check:
            players = []
            for pl in self.teams()["free"]:
                players.append(dict(name=pl.clean_name, score=pl.stats.score, kills=pl.stats.kills, deaths=pl.stats.deaths, dg=pl.stats.damage_dealt, dr=pl.stats.damage_taken, time=int(pl.stats.time / 60000)))
            output = ["{:^31} | {:^6} | {:^4} | {:^4} | {:^6} | {:^6} | {}".format("Name", "Scr", "Kll", "Dth", "DG", "DR", "Time")]
            for p in sorted(players, key=itemgetter("kills"), reverse=True):
                output.append("{name:^31} | {score:^6} | {kills:^4} | {deaths:^4} | {dg:^6} | {dr:^6} | {time}min".format(**p))
            for count, line in enumerate(output, start=1):
                player.tell(line)
        else:
            red_players = []
            red_kills = 0
            red_deaths = 0
            red_dg = 0
            red_dr = 0
            blue_players = []
            blue_kills = 0
            blue_deaths = 0
            blue_dg = 0
            blue_dr = 0

            for pl in self.teams()["red"]:
                red_players.append(dict(team=pl.team, name=pl.clean_name, score=pl.stats.score, kills=pl.stats.kills, deaths=pl.stats.deaths, dg=pl.stats.damage_dealt, dr=pl.stats.damage_taken, time=int(pl.stats.time / 60000)))
                red_kills += pl.stats.kills
                red_deaths += pl.stats.deaths
                red_dg += pl.stats.damage_dealt
                red_dr += pl.stats.damage_taken

            for pl in self.teams()["blue"]:
                blue_players.append(dict(team=pl.team, name=pl.clean_name, score=pl.stats.score, kills=pl.stats.kills, deaths=pl.stats.deaths, dg=pl.stats.damage_dealt, dr=pl.stats.damage_taken, time=int(pl.stats.time / 60000)))
                blue_kills += pl.stats.kills
                blue_deaths += pl.stats.deaths
                blue_dg += pl.stats.damage_dealt
                blue_dr += pl.stats.damage_taken

            red_output = ["{:^4} | {:^31} | {:^6} | {:^4} | {:^4} | {:^6} | {:^6} | {}".format("Team", "Name", "Scr", "Kll", "Dth", "DG", "DR", "Time")]
            blue_output = ["{:^4} | {:^31} | {:^6} | {:^4} | {:^4} | {:^6} | {:^6} | {}".format("Team", "Name", "Scr", "Kll", "Dth", "DG", "DR", "Time")]

            for p in sorted(red_players, key=itemgetter("kills"), reverse=True):
                red_output.append("^1{team:^4} ^7| {name:^31} | {score:^6} | {kills:^4} | {deaths:^4} | {dg:^6} | {dr:^6} | {time}min".format(**p))
            for p in sorted(blue_players, key=itemgetter("kills"), reverse=True):
                blue_output.append("^4{team:^4} ^7| {name:^31} | {score:^6} | {kills:^4} | {deaths:^4} | {dg:^6} | {dr:^6} | {time}min".format(**p))

            if self.game.red_score > self.game.blue_score:
                for count, line in enumerate(red_output, start=1):
                    player.tell(line)
                player.tell("^1{:^4} ^7| ^5{:^31} ^7| {:^6} | {:^4} | {:^4} | {:^6} | {:^6} |".format("red", "Totals", self.game.red_score, red_kills, red_deaths, red_dg, red_dr))
                player.tell("^3---------------------------------------------------------------------------------------")
                for count, line in enumerate(blue_output, start=1):
                    player.tell(line)
                player.tell("^4{:^4} ^7| ^5{:^31} ^7| {:^6} | {:^4} | {:^4} | {:^6} | {:^6} |".format("blue", "Totals", self.game.blue_score, blue_kills, blue_deaths, blue_dg, blue_dr))
            else:
                for count, line in enumerate(blue_output, start=1):
                    player.tell(line)
                player.tell("^4{:^4} ^7| ^5{:^31} ^7| {:^6} | {:^4} | {:^4} | {:^6} | {:^6} |".format("blue", "Totals", self.game.blue_score, blue_kills, blue_deaths, blue_dg, blue_dr))
                player.tell("^3---------------------------------------------------------------------------------------")
                for count, line in enumerate(red_output, start=1):
                    player.tell(line)
                player.tell("^1{:^4} ^7| ^5{:^31} ^7| {:^6} | {:^4} | {:^4} | {:^6} | {:^6} |".format("red", "Totals", self.game.red_score, red_kills, red_deaths, red_dg, red_dr))
