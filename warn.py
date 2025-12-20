# warn.py by x0rnn, a plugin to warn players for misbehaving. A warning is removed after X days (qlx_warnDays), unless the player has been warned X times (qlx_maxStrikes), then he is perma-banned.
# When a warned player joins a server, everyone is notified about him and the reason he was warned.
# !warn <id> <reason>
# !unwarn <id> <warnings to remove>
# !warned (to list all warned players)
#
# Changelog:
# 2025-11-24: Fixed redis-py 3.0+ compatibility (zadd syntax)
# 2025-12-20: Fixed multiple bugs:
#   - Fixed critical bug in is_warned() where zrangebyscore result was treated as dict
#   - Fixed bytes vs string issues with redis-py 3.0+ (member decoding)
#   - Fixed hgetall() bytes keys issue
#   - Replaced deprecated hmset() with hset(mapping=)
#   - Added better error handling throughout

import minqlx
import time
import datetime

PLAYER_KEY = "minqlx:players:{}"
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def decode_if_bytes(value):
    """Helper to decode bytes to string if necessary (redis-py 3.0+ compatibility)"""
    if isinstance(value, bytes):
        return value.decode('utf-8')
    return value


def decode_dict(d):
    """Helper to decode a dictionary with potentially bytes keys/values"""
    if d is None:
        return {}
    return {decode_if_bytes(k): decode_if_bytes(v) for k, v in d.items()}


class warn(minqlx.Plugin):
    
    def __init__(self):
        self.add_hook("player_connect", self.handle_player_connect, priority=minqlx.PRI_HIGH)
        self.add_hook("player_loaded", self.handle_player_loaded)
        self.add_command("warn", self.cmd_warn, 4, usage="<id> <reason>")
        self.add_command("unwarn", self.cmd_unwarn, 5, usage="<id> <warnings to remove>")
        self.add_command("warned", self.cmd_warned, 4)

        self.set_cvar_once("qlx_warnDays", "7") #how many days until the warning goes away (each additional warn adds this many days to the previous expiration date)
        self.set_cvar_once("qlx_maxStrikes", "3") #how many strikes before getting banned

    def handle_player_connect(self, player):
        warned = self.is_warned(player.steam_id)
        if warned:
            strike, reason, expires = warned
            if strike >= self.get_cvar("qlx_maxStrikes", int):
                return "You are banned for repeated violations: {}: warned {} times.".format(reason, strike)

    def handle_player_loaded(self, player):
        warned = self.is_warned(player.steam_id)
        if warned:
            strike, reason, expires = warned
            self.msg("^1Attention^7! {} connected. Warned for: ^6{}^7, strike: ^6{}^7/^6{}^7, expires: ^6{}^7.".format(player.name, reason, strike, self.get_cvar("qlx_maxStrikes", int), expires))

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
        td = datetime.timedelta(days=self.get_cvar("qlx_warnDays", int))

        try:
            previous_warn = self.db.zrangebyscore(PLAYER_KEY.format(ident) + ":warnings", time.time(), "+inf", withscores=True)
        except (ValueError, Exception):
            previous_warn = []

        if previous_warn:
            # Decode the warn_id from bytes if necessary
            prev_warn_id = decode_if_bytes(previous_warn[-1][0])
            longest_warn = decode_dict(self.db.hgetall(PLAYER_KEY.format(ident) + ":warnings" + ":{}".format(prev_warn_id)))
            if longest_warn and "expires" in longest_warn:
                previous_expire = datetime.datetime.strptime(longest_warn["expires"], TIME_FORMAT)
                expires = (previous_expire + td).strftime(TIME_FORMAT)
            else:
                expires = (datetime.datetime.now() + td).strftime(TIME_FORMAT)
        else:
            expires = (datetime.datetime.now() + td).strftime(TIME_FORMAT)

        now = datetime.datetime.now().strftime(TIME_FORMAT)
        base_key = PLAYER_KEY.format(ident) + ":warnings"
        warn_id = self.db.zcard(base_key)
        db = self.db.pipeline()
        # FIXED: Changed zadd syntax for redis-py 3.0+ compatibility
        db.zadd(base_key, {str(warn_id): time.time() + td.total_seconds()})
        db.incr(PLAYER_KEY.format(ident) + ":warnings:strikes")
        warn_data = {"expires": expires, "reason": reason, "issued": now, "issued_by": str(player.steam_id)}
        # FIXED: Using hset with mapping instead of deprecated hmset
        db.hset(base_key + ":{}".format(warn_id), mapping=warn_data)
        db.execute()
        if strike + 1 < self.get_cvar("qlx_maxStrikes", int):
            self.msg("{} has been warned for: ^6{}^7, strike: ^6{}^7/^6{}^7, expires: ^6{}^7.".format(name, reason, strike + 1, self.get_cvar("qlx_maxStrikes", int), expires))
        elif strike + 1 >= self.get_cvar("qlx_maxStrikes", int):
            try:
                self.kick(ident, "Banned for repeated violations: {}: warned {} times.".format(reason, strike + 1))
            except ValueError:
                self.msg("^6{} ^7has been banned for repeated violations: ^6{}^7: warned ^6{} ^7times.".format(name, reason, strike + 1))

    def cmd_unwarn(self, player, msg, channel):
        if len(msg) < 2:
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

        base_key = PLAYER_KEY.format(ident)
        
        try:
            strikes = int(self.db[base_key + ":warnings:strikes"])
        except KeyError:
            strikes = 0
        
        if strikes <= 0:
            channel.reply("^6{}^7 has no warnings to remove.".format(name))
            return

        if len(msg) == 2:
            strikes_to_forgive = 1
        else:
            try:
                strikes_to_forgive = int(msg[2])
            except ValueError:
                channel.reply("Unintelligible number of warnings to forgive. Please use numbers.")
                return

        new_strikes = strikes - strikes_to_forgive
        if new_strikes <= 0:
            self.db[base_key + ":warnings:strikes"] = 0
            channel.reply("^6{}^7's warnings have been reduced to ^60^7.".format(name))
        else:
            self.db[base_key + ":warnings:strikes"] = new_strikes
            channel.reply("^6{}^7 warnings have been forgiven, putting ^6{}^7 at ^6{}^7 warnings."
                .format(strikes_to_forgive, name, new_strikes))

    def cmd_warned(self, player, msg, channel):
        playerlist = self.db.keys("minqlx:players:*:warnings:strikes")
        tmp2 = ""

        for sublist in playerlist:
            # Decode bytes if necessary
            sublist_str = decode_if_bytes(sublist)
            tmp = sublist_str.split(":")
            tmp2 += str(tmp[2]) + ","
        tmp2 = tmp2[:-1]
        
        if not tmp2:
            player.tell("^2No warned players found.")
            return
        
        steamids_list = tmp2.split(",")
        player.tell("^2Warned players:\n")
        
        for steamid in steamids_list:
            id_name = self.db.lindex(PLAYER_KEY.format(steamid), 0)
            if id_name:
                id_name = decode_if_bytes(id_name)
            active = self.db.zrangebyscore(PLAYER_KEY.format(steamid) + ":warnings", time.time(), "+inf", withscores=True)
            if active:
                try:
                    strike = int(self.db[PLAYER_KEY.format(steamid) + ":warnings:strikes"])
                except (KeyError, ValueError):
                    strike = 0
                if strike:
                    # Decode the warn_id from bytes if necessary
                    active_warn_id = decode_if_bytes(active[-1][0])
                    longest_warn = decode_dict(self.db.hgetall(PLAYER_KEY.format(steamid) + ":warnings" + ":{}".format(active_warn_id)))
                    if longest_warn:
                        reason = longest_warn.get("reason", "Unknown")
                        expires = longest_warn.get("expires", "Unknown")
                        if strike >= self.get_cvar("qlx_maxStrikes", int):
                            player.tell("^1Banned^7: {} ^7({}): ^6{}^7,^6 {}^7/^6{}^7.".format(id_name, steamid, reason, strike, self.get_cvar("qlx_maxStrikes", int)))
                        else:
                            player.tell("{} ^7({}): ^6{}^7,^6 {}^7/^6{}^7, expires: ^6{}^7.".format(id_name, steamid, reason, strike, self.get_cvar("qlx_maxStrikes", int), expires))

    def is_warned(self, steam_id):
        try:
            strike = int(self.db[PLAYER_KEY.format(steam_id) + ":warnings:strikes"])
        except KeyError:
            strike = 0

        if strike > 0:
            warn_list = self.db.zrangebyscore(PLAYER_KEY.format(steam_id) + ":warnings", time.time(), "+inf", withscores=True)
            
            if not warn_list and strike < self.get_cvar("qlx_maxStrikes", int):
                # Warnings have expired and player is below max strikes - clear their strikes
                self.db.incrby(PLAYER_KEY.format(steam_id) + ":warnings:strikes", -strike)
                return None
            
            elif not warn_list and strike >= self.get_cvar("qlx_maxStrikes", int):
                # Player has max strikes but active warnings expired - they're still banned
                # Get any warning to show the reason (even expired ones)
                all_warns = self.db.zrangebyscore(PLAYER_KEY.format(steam_id) + ":warnings", "-inf", "+inf", withscores=True)
                if all_warns:
                    # FIXED: all_warns is a list of tuples [(member, score), ...], not a dict!
                    # Get the last warning's data from the hash
                    last_warn_id = decode_if_bytes(all_warns[-1][0])
                    longest_warn = decode_dict(self.db.hgetall(PLAYER_KEY.format(steam_id) + ":warnings" + ":{}".format(last_warn_id)))
                    if longest_warn and "expires" in longest_warn and "reason" in longest_warn:
                        expires = datetime.datetime.strptime(longest_warn["expires"], TIME_FORMAT)
                        return strike, longest_warn["reason"], expires
                # Fallback if we can't get the warning details
                return strike, "Multiple violations", datetime.datetime.now()
            
            elif warn_list:
                # Player has active (non-expired) warnings
                warn_id = decode_if_bytes(warn_list[-1][0])
                longest_warn = decode_dict(self.db.hgetall(PLAYER_KEY.format(steam_id) + ":warnings" + ":{}".format(warn_id)))
                if longest_warn and "expires" in longest_warn and "reason" in longest_warn:
                    expires = datetime.datetime.strptime(longest_warn["expires"], TIME_FORMAT)
                    if (expires - datetime.datetime.now()).total_seconds() > 0:
                        return strike, longest_warn["reason"], expires

        return None
