# checkplayers.py by x0rnn, a plugin to list all players with permission >= 1, banned, leaver-banned, leaver-warned and silenced players
# !permissions
# !banned
# !leaverbanned
# !leaverwarned
# !silenced

import minqlx
import time
import datetime

PLAYER_KEY = "minqlx:players:{}"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class checkplayers(minqlx.Plugin):
    
    def __init__(self):
        self.add_command("silenced", self.cmd_silenced, 4)
        self.add_command("banned", self.cmd_banned, 4)
        self.add_command("permissions", self.cmd_permissions, 4)
        self.add_command("leaverbanned", self.cmd_leaverbanned, 4)
        self.add_command("leaverwarned", self.cmd_leaverwarned, 4)

        self.adminlist = []

    def cmd_silenced(self, player, msg, channel):
        playerlist = self.db.keys("minqlx:players:*:silences")
        tmp = ""
        tmp2 = ""

        for sublist in playerlist:
            tmp = str(sublist).split(":")
            tmp2 += str(tmp[2]) + ","
        tmp2.split(",")
        tmp2 = tmp2[:-1]
        
        i = 0
        player.tell("^2Silenced players:\n")
        for steamids in playerlist:
            steamids = tmp2.split(",")
            id_name = self.db.lindex(PLAYER_KEY.format(steamids[i]), 0)
            active = self.db.zrangebyscore(PLAYER_KEY.format(steamids[i]) + ":silences", time.time(), "+inf", withscores=True)
            if active:
                longest_silence = self.db.hgetall(PLAYER_KEY.format(steamids[i]) + ":silences" + ":{}".format(active[-1][0]))
                expires = datetime.datetime.strptime(longest_silence["expires"], TIME_FORMAT)
                reason = longest_silence["reason"]
                if (expires - datetime.datetime.now()).total_seconds() > 0:
                    if reason:
                        player.tell("{} ^7({}): ^6{}^7:^6 {}^7.".format(id_name, steamids[i], expires, reason))
                    else:
                        player.tell("{} ^7({}): ^6{}^7.".format(id_name, steamids[i], expires))
            i += 1

    def cmd_banned(self, player, msg, channel):
        playerlist = self.db.keys("minqlx:players:*:bans")
        tmp = ""
        tmp2 = ""

        for sublist in playerlist:
            tmp = str(sublist).split(":")
            tmp2 += str(tmp[2]) + ","
        tmp2.split(",")
        tmp2 = tmp2[:-1]

        i = 0
        player.tell("^2Banned players:\n")
        for steamids in playerlist:
            steamids = tmp2.split(",")
            id_name = self.db.lindex(PLAYER_KEY.format(steamids[i]), 0)
            active = self.db.zrangebyscore(PLAYER_KEY.format(steamids[i]) + ":bans", time.time(), "+inf", withscores=True)
            if active:
                longest_ban = self.db.hgetall(PLAYER_KEY.format(steamids[i]) + ":bans" + ":{}".format(active[-1][0]))
                expires = datetime.datetime.strptime(longest_ban["expires"], TIME_FORMAT)
                reason = longest_ban["reason"]
                if (expires - datetime.datetime.now()).total_seconds() > 0:
                    if reason:
                        player.tell("{} ^7({}): ^6{}^7:^6 {}^7.".format(id_name, steamids[i], expires, reason))
                    else:
                        player.tell("{} ^7({}): ^6{}^7.".format(id_name, steamids[i], expires))
            i += 1

    def cmd_permissions(self, player, msg, channel):
        playerlist = self.db.keys("minqlx:players:*:permission")
        tmp = ""
        tmp2 = ""

        for sublist in playerlist:
            tmp = str(sublist).split(":")
            tmp2 += str(tmp[2]) + ","
        tmp2.split(",")
        tmp2 = tmp2[:-1]

        i = 0
        player.tell("^2Permission levels:\n")
        for steamids in playerlist:
            steamids = tmp2.split(",")
            if self.db.has_permission(steamids[i], 1):
                id_name = self.db.lindex(PLAYER_KEY.format(steamids[i]), 0)
                perm = self.db.get(PLAYER_KEY.format(steamids[i]) + ":permission")
                self.adminlist.append((id_name, steamids[i], perm))
            i += 1

        self.adminlist.sort(key=lambda p: p[2], reverse=True)
        if not str(minqlx.owner()) in (item[1] for item in self.adminlist):
            owner_name = self.db.lindex(PLAYER_KEY.format(minqlx.owner()), 0)
            self.adminlist.insert(0, (owner_name, str(minqlx.owner()), "5"))
        for id_name, steamid, perm in self.adminlist:
            player.tell("{} ^7({}) - ^2Level^7: ^6{}^7.".format(id_name, steamid, perm))
        self.adminlist = []

    def cmd_leaverbanned(self, player, msg, channel):
        if not self.get_cvar("qlx_leaverBan", bool):
            return None

        playerlist = self.db.keys("minqlx:players:*:games_left")
        tmp = ""
        tmp2 = ""

        for sublist in playerlist:
            tmp = str(sublist).split(":")
            tmp2 += str(tmp[2]) + ","
        tmp2.split(",")
        tmp2 = tmp2[:-1]

        min_games_completed = self.get_cvar("qlx_leaverBanMinimumGames", int)
        warn_threshold = self.get_cvar("qlx_leaverBanWarnThreshold", float)
        ban_threshold = self.get_cvar("qlx_leaverBanThreshold", float)

        i = 0
        player.tell("^2Leaver-banned players:\n")
        for steamids in playerlist:
            steamids = tmp2.split(",")
            left = int(self.db[PLAYER_KEY.format(steamids[i]) + ":games_left"])
            if left:
                try:
                    completed = self.db[PLAYER_KEY.format(steamids[i]) + ":games_completed"]
                except KeyError:
                    completed = 0
                completed = int(completed)
                total = completed + left
                if total < min_games_completed:
                    ratio = (completed + (min_games_completed - total)) / min_games_completed
                else:
                    ratio = completed / total
                if ratio <= ban_threshold and total >= min_games_completed:
                    id_name = self.db.lindex(PLAYER_KEY.format(steamids[i]), 0)
                    player.tell("{} ^7({}) - ^2Left^7: ^6{}^7, ^2completed^7: ^6{} ^7({}%).".format(id_name, steamids[i], left, completed, round((completed / total) * 100)))
            i += 1

    def cmd_leaverwarned(self, player, msg, channel):
        if not self.get_cvar("qlx_leaverBan", bool):
            return None

        playerlist = self.db.keys("minqlx:players:*:games_left")
        tmp = ""
        tmp2 = ""

        for sublist in playerlist:
            tmp = str(sublist).split(":")
            tmp2 += str(tmp[2]) + ","
        tmp2.split(",")
        tmp2 = tmp2[:-1]

        min_games_completed = self.get_cvar("qlx_leaverBanMinimumGames", int)
        warn_threshold = self.get_cvar("qlx_leaverBanWarnThreshold", float)
        ban_threshold = self.get_cvar("qlx_leaverBanThreshold", float)

        i = 0
        player.tell("^2Leaver-warned players:\n")
        for steamids in playerlist:
            steamids = tmp2.split(",")
            left = int(self.db[PLAYER_KEY.format(steamids[i]) + ":games_left"])
            if left:
                try:
                    completed = self.db[PLAYER_KEY.format(steamids[i]) + ":games_completed"]
                except KeyError:
                    completed = 0
                completed = int(completed)
                total = completed + left
                if total < min_games_completed:
                    ratio = (completed + (min_games_completed - total)) / min_games_completed
                else:
                    ratio = completed / total
                if ratio <= warn_threshold and (ratio > ban_threshold or total < min_games_completed):
                    id_name = self.db.lindex(PLAYER_KEY.format(steamids[i]), 0)
                    player.tell("{} ^7({}) - ^2Left^7: ^6{}^7, ^2completed^7: ^6{} ^7({} percent).".format(id_name, steamids[i], left, completed, round((completed / total) * 100)))
            i += 1
