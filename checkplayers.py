# checkplayers.py, a plugin to list all banned (excluding leaverbanned) and silenced players

import minqlx
import time
import datetime

PLAYER_KEY = "minqlx:players:{}"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class checkplayers(minqlx.Plugin):
    
    def __init__(self):
        self.add_command("silenced", self.cmd_silenced, 4)
        self.add_command("banned", self.cmd_banned, 4)

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
            id_name = self.db.lindex(PLAYER_KEY.format(steamids[i]), -1)
            active = self.db.zrangebyscore(PLAYER_KEY.format(steamids[i]) + ":silences", time.time(), "+inf", withscores=True)
            if active:
                longest_silence = self.db.hgetall(PLAYER_KEY.format(steamids[i]) + ":silences" + ":{}".format(active[-1][0]))
                expires = datetime.datetime.strptime(longest_silence["expires"], TIME_FORMAT)
                reason = longest_silence["reason"]
                if (expires - datetime.datetime.now()).total_seconds() > 0:
                    if reason:
                        player.tell("^6{} ^7(^6{}^7): ^6{}^7:^6 {}^7.".format(steamids[i], id_name, expires, reason))
                    else:
                        player.tell("^6{} ^7(^6{}^7): ^6{}^7.".format(steamids[i], id_name, expires))
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
            id_name = self.db.lindex(PLAYER_KEY.format(steamids[i]), -1)
            active = self.db.zrangebyscore(PLAYER_KEY.format(steamids[i]) + ":bans", time.time(), "+inf", withscores=True)
            if active:
                longest_ban = self.db.hgetall(PLAYER_KEY.format(steamids[i]) + ":bans" + ":{}".format(bans[-1][0]))
                expires = datetime.datetime.strptime(longest_ban["expires"], TIME_FORMAT)
                reason = longest_ban["reason"]
                if (expires - datetime.datetime.now()).total_seconds() > 0:
                    if reason:
                        player.tell("^6{} ^7(^6{}^7): ^6{}^7:^6 {}^7.".format(steamids[i], id_name, expires, reason))
                    else:
                        player.tell("^6{} ^7(^6{}^7): ^6{}^7.".format(steamids[i], id_name, expires))
            i += 1
