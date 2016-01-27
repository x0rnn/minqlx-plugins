# warn.py by x0rnn, a plugin to warn players for misbehaving. A warning is removed after X days, unless the player has been warned X times, then he is perma-banned.
# todo: !unwarn, !listwarned

import minqlx
import time
import datetime

PLAYER_KEY = "minqlx:players:{}"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

class warn(minqlx.Plugin):
    
    def __init__(self):
        self.add_hook("player_connect", self.handle_player_connect, priority=minqlx.PRI_HIGH)
        self.add_hook("player_loaded", self.handle_player_loaded)
        self.add_command("warn", self.cmd_warn, 4, usage="<id> <reason>")

        self.days = 7 #how many days until the warning goes away
        self.max_strikes = 3 #how many strikes before getting banned

    def handle_player_connect(self, player):
        warned = self.is_warned(player.steam_id)
        if warned:
            strike, reason = warned
            if strike >= self.max_strikes:
                return "You are banned for repeated violations: {}: warned {} times.".format(reason, strike)

    def handle_player_loaded(self, player):
        warned = self.is_warned(player.steam_id)
        if warned:
            strike, reason = warned
            self.msg("^1Attention^7! {} connected. Warned for: ^6{}^7. Strike ^6{}^7/^6{}^7.".format(player.name, reason, strike, self.max_strikes))

    def cmd_warn(self, player, msg, channel):
        if len(msg) < 3:
            return minqlx.RET_USAGE

        try:
            ident = int(msg[1])
            target_player = None
            if 0 <= ident < 64:
                target_player = self.player(ident)
                ident = target_player.steam_id
        except ValueError:
            channel.reply("Invalid ID. Use either a client ID or a SteamID64.")
            return
        except minqlx.NonexistentPlayerError:
            channel.reply("Invalid client ID. Use either a client ID or a SteamID64.")
            return
        
        if target_player:
            name = target_player.name
        else:
            name = ident

        if self.db.has_permission(ident, 5):
            channel.reply("^6{}^7 has permission level 5 and cannot be warned.".format(name))
            return

        try:
            strike = int(self.db[PLAYER_KEY.format(ident) + ":warnings:strikes"])
        except KeyError:
            strike = 0

        reason = " ".join(msg[2:])
        td = datetime.timedelta(days=self.days)
        now = datetime.datetime.now().strftime(TIME_FORMAT)
        expires = (datetime.datetime.now() + td).strftime(TIME_FORMAT)
        base_key = PLAYER_KEY.format(ident) + ":warnings"
        warn_id = self.db.zcard(base_key)
        db = self.db.pipeline()
        db.zadd(base_key, time.time() + td.total_seconds(), warn_id)
        db.incr(PLAYER_KEY.format(ident) + ":warnings:strikes")
        warn = {"expires": expires, "reason": reason, "issued": now, "issued_by": player.steam_id}
        db.hmset(base_key + ":{}".format(warn_id), warn)
        db.execute()
        if strike + 1 < self.max_strikes:
            self.msg("{} has been warned for: ^6{}^7, strike number: ^6{}^7/^6{}^7.".format(name, reason, strike + 1, self.max_strikes))
        elif strike + 1 >= self.max_strikes:
            try:
                self.kick(ident, "Banned for repeated violations: {}: warned {} times.".format(reason, strike + 1))
            except ValueError:
                self.msg("^6{} ^7has been banned for repeated violations: ^6{}^7: warned ^6{} ^7times.".format(name, strike + 1))

    def is_warned(self, steam_id):
        try:
            strike = int(self.db[PLAYER_KEY.format(steam_id) + ":warnings:strikes"])
        except KeyError:
            strike = 0

        if strike > 0:
            warn = self.db.zrangebyscore(PLAYER_KEY.format(steam_id) + ":warnings", time.time(), "+inf", withscores=True)
            if not warn and strike < self.max_strikes:
                self.db.incrby(PLAYER_KEY.format(steam_id) + ":warnings:strikes", -strike)
                return None
            elif not warn and strike >= self.max_strikes:
                previous_warn = self.db.zrangebyscore(PLAYER_KEY.format(steam_id) + ":warnings", "-inf", "+inf", withscores=True)
                longest_warn = self.db.hgetall(PLAYER_KEY.format(steam_id) + ":warnings" + ":{}".format(previous_warn[-1][0]))
                return strike, longest_warn["reason"]
            elif warn:
                longest_warn = self.db.hgetall(PLAYER_KEY.format(steam_id) + ":warnings" + ":{}".format(warn[-1][0]))
                expires = datetime.datetime.strptime(longest_warn["expires"], TIME_FORMAT)
                if (expires - datetime.datetime.now()).total_seconds() > 0:
                    return strike, longest_warn["reason"]

        return None
