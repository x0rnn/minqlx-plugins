# killingspree.py by x0rnn
# Unreal Tournament sound announcements for:
#
# 	5 kills in a row: killing spree
# 	10 kills in a row: rampage
# 	15 kills in a row: dominating
# 	20 kills in a row: unstoppable
# 	25 kills in a row: godlike
# 	30 kills in a row: wicked sick
#
# 	3 kills in 3 second intervals: multikill
# 	4 kills in 4 second intervals: mega kill
# 	5 kills in 4 second intervals: ultra kill
# 	6 kills in 4 second intervals: monster kill
# 	7 kills in 4 second intervals: ludicrous kill
# 	8 kills in 4 second intervals: holy shit
#
# !spree_record will print the current map's killing spree record and the player's name
# !multikills will print your multikill stats (multikills, megakills, ultrakills, etc.)
# !clear_spree_record will clear the current map record (admins only)
#
# Selfkilling or switching teams will nullify your killing streak and it won't register as a record either.
#
# Use with: https://steamcommunity.com/sharedfiles/filedetails/?id=701783942
# Add 701783942 to qlx_workshopReferences and workshop.txt

import minqlx
import time
from collections import defaultdict

SPREE_KEY = "minqlx:spree:{}"
PLAYER_KEY = "minqlx:spree:players:{}"

class killingspree(minqlx.Plugin):
    def __init__(self):
        self.add_hook("death", self.handle_death)
        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("round_end", self.handle_round_end)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("player_spawn", self.handle_player_spawn)
        self.add_hook("game_countdown", self.handle_game_countdown)
        self.add_hook("round_countdown", self.handle_round_countdown)
        self.add_hook("map", self.handle_map)
        self.add_command("spree_record", self.cmd_spree_record)
        self.add_command("multikills", self.cmd_multikills)
        self.add_command("clear_spree_record", self.cmd_clear_spree_record, 5)

        self.kspree = {}
        self.record = 0
        self.multikill = defaultdict(dict)

    def handle_player_spawn(self, player):
        self.kspree[str(player.steam_id)] = 0
        self.multikill[str(player.steam_id)][0] = 0
        self.multikill[str(player.steam_id)][1] = 0

    def handle_game_countdown(self):
        self.kspree.clear()

    def handle_round_countdown(self):
        self.kspree.clear()

    def handle_player_disconnect(self, player, reason):
        if str(player.steam_id) in self.kspree:
            self.kspree[str(player.steam_id)] = 0

    def handle_death(self, victim, killer, data):
        if self.game.state != 'in_progress':
            return
        else:
            map_name = self.game.map.lower()
            def checkKSpree(id, name):
                if self.kspree[id] % 5 == 0:
                    spree_id = self.kspree[id]
                    if spree_id == 5:
                        spree_msg = "is on a killing spree!"
                        self.play_sound("sound/misc/killingspree.wav")
                        msg = "{} {} ^1{} ^7kills in a row!".format(name, spree_msg, self.kspree[id])
                        self.msg(msg)
                    elif spree_id == 10:
                        spree_msg = "is on a rampage!"
                        self.play_sound("sound/misc/rampage.wav")
                        msg = "{} {} ^1{} ^7kills in a row!".format(name, spree_msg, self.kspree[id])
                        self.msg(msg)
                    elif spree_id == 15:
                        spree_msg = "is dominating!"
                        self.play_sound("sound/misc/dominating.wav")
                        msg = "{} {} ^1{} ^7kills in a row!".format(name, spree_msg, self.kspree[id])
                        self.msg(msg)
                    elif spree_id == 20:
                        spree_msg = "is unstoppable!"
                        self.play_sound("sound/misc/unstoppable.wav")
                        msg = "{} {} ^1{} ^7kills in a row!".format(name, spree_msg, self.kspree[id])
                        self.msg(msg)
                    elif spree_id == 25:
                        spree_msg = "is godlike!"
                        self.play_sound("sound/misc/godlike.wav")
                        msg = "{} {} ^1{} ^7kills in a row!".format(name, spree_msg, self.kspree[id])
                        self.msg(msg)
                    elif spree_id >= 30:
                        spree_msg = "is wicked sick!"
                        self.play_sound("sound/misc/wickedsick.wav")
                        msg = "{} {} ^1{} ^7kills in a row!".format(name, spree_msg, self.kspree[id])
                        self.msg(msg)

            def checkKSpreeEnd(id, v_name, k_name, normal_kill):
                if id in self.kspree and self.kspree[id] >= 5:
                    if normal_kill:
                        if self.kspree[id] > self.record:
                            self.db.zadd(SPREE_KEY.format(map_name), self.kspree[id], "{},{}".format(id, int(time.time())))
                            msg = "{}'s killing spree ended (^1{} ^7kills), killed by {}.".format(v_name, self.kspree[id], k_name)
                            self.msg(msg)
                            self.msg("This is a new map record!")
                        else:
                            msg = "{}'s killing spree ended (^1{} ^7kills), killed by {}.".format(v_name, self.kspree[id], k_name)
                            self.msg(msg)
                    else:
                        if data['KILLER'] is None:
                            if self.kspree[id] > self.record:
                                self.db.zadd(SPREE_KEY.format(map_name), self.kspree[id], "{},{}".format(id, int(time.time())))
                                msg = "{}'s killing spree ended (^1{} ^7kills), killed by the world.".format(v_name, self.kspree[id])
                                self.msg(msg)
                                self.msg("This is a new map record!")
                            else:
                                msg = "{}'s killing spree ended (^1{} ^7kills), killed by the world.".format(v_name, self.kspree[id])
                                self.msg(msg)
                        else:
                            if self.kspree[id] > self.record:
                                self.db.zadd(SPREE_KEY.format(map_name), self.kspree[id], "{},{}".format(id, int(time.time())))
                                msg = "{}'s killing spree ended (^1{} ^7kills), teamkilled by {}.".format(v_name, self.kspree[id], k_name)
                                self.msg(msg)
                                self.msg("This is a new map record!")
                            else:
                                msg = "{}'s killing spree ended (^1{} ^7kills), teamkilled by {}.".format(v_name, self.kspree[id], k_name)
                                self.msg(msg)

            def checkMultiKill(id, k_name):
                 current_time = time.time()
                 multikill_threshold_time = current_time - self.multikill[id][0]
                 if multikill_threshold_time < 4:
                     self.multikill[id][1] = self.multikill[id][1] + 1
                     if multikill_threshold_time < 3:
                         if self.multikill[id][1] == 3:
                             if not self.db.lrange(PLAYER_KEY.format(id) + ":multikills", 0, -1):
                                 self.db.lpush(PLAYER_KEY.format(id) + ":multikills", 0, 0, 0, 0, 0, 0)
                                 mk = 0
                             else:
                                 mk = int(self.db.lindex(PLAYER_KEY.format(id) + ":multikills", 0))
                             mk = mk + 1
                             self.play_sound("sound/misc/multikill.wav")
                             self.msg("!!! ^1Multi kill ^7> {} < ^1Multi kill ^7!!! ({} kills)".format(k_name, self.multikill[id][1]))
                             self.db.lset(PLAYER_KEY.format(id) + ":multikills", 0, mk)
                     if self.multikill[id][1] == 4:
                         if not self.db.lrange(PLAYER_KEY.format(id) + ":multikills", 0, -1):
                             self.db.lpush(PLAYER_KEY.format(id) + ":multikills", 0, 0, 0, 0, 0, 0)
                             mk = 0
                         else:
                             mk = int(self.db.lindex(PLAYER_KEY.format(id) + ":multikills", 1))
                         mk = mk + 1
                         self.play_sound("sound/misc/megakill.ogg")
                         self.msg("!!! ^1Mega kill ^7> {} < ^1Mega kill ^7!!! ({} kills)".format(k_name, self.multikill[id][1]))
                         self.db.lset(PLAYER_KEY.format(id) + ":multikills", 1, mk)
                     elif self.multikill[id][1] == 5:
                         mk = int(self.db.lindex(PLAYER_KEY.format(id) + ":multikills", 2))
                         mk = mk + 1
                         self.play_sound("sound/misc/ultrakill.ogg")
                         self.msg("!!! ^1ULTRA KILL ^7> {} < ^1ULTRA KILL ^7!!! ({} kills)".format(k_name, self.multikill[id][1]))
                         self.db.lset(PLAYER_KEY.format(id) + ":multikills", 2, mk)
                     elif self.multikill[id][1] == 6:
                         mk = int(self.db.lindex(PLAYER_KEY.format(id) + ":multikills", 3))
                         mk = mk + 1
                         self.play_sound("sound/misc/monsterkill.wav")
                         self.msg("!!! ^1MONSTER KILL ^7> {} < ^1MONSTER KILL^7!!! ({} kills)".format(k_name, self.multikill[id][1]))
                         self.db.lset(PLAYER_KEY.format(id) + ":multikills", 3, mk)
                     elif self.multikill[id][1] == 7:
                         mk = int(self.db.lindex(PLAYER_KEY.format(id) + ":multikills", 4))
                         mk = mk + 1
                         self.play_sound("sound/misc/ludicrouskill.wav")
                         self.msg("!!! ^1LUDICROUS KILL ^7> {} < ^1LUDICROUS KILL ^7!!! ({} kills)".format(k_name, self.multikill[id][1]))
                         self.db.lset(PLAYER_KEY.format(id) + ":multikills", 4, mk)
                     elif self.multikill[id][1] == 8:
                         mk = int(self.db.lindex(PLAYER_KEY.format(id) + ":multikills", 5))
                         mk = mk + 1
                         self.play_sound("sound/misc/holyshit.ogg")
                         self.msg("!!! ^1 H O L Y  S H I T ^7> {} < ^1H O L Y  S H I T ^7!!! ({} kills)".format(k_name, self.multikill[id][1]))
                         self.db.lset(PLAYER_KEY.format(id) + ":multikills", 5, mk)
                 else:
                     self.multikill[id][1] = 1
                 self.multikill[id][0] = time.time()

            v_id = data['VICTIM']['STEAM_ID']
            v_name = data['VICTIM']['NAME']

            if data['KILLER'] is not None and not data['TEAMKILL']: #normal kill
                k_id = data['KILLER']['STEAM_ID']
                k_name = data['KILLER']['NAME']
                self.kspree[k_id] = self.kspree[k_id] + 1
                checkKSpree(k_id, k_name)
                checkMultiKill(k_id, k_name)
                checkKSpreeEnd(v_id, v_name, k_name, True)

            elif data['TEAMKILL']: #teamkill
                k_name = data['KILLER']['NAME']
                checkKSpreeEnd(v_id, v_name, k_name, False)

            elif data['KILLER'] is None: #killed by world
                checkKSpreeEnd(v_id, v_name, "world", False)

    def handle_game_end(self, data):
        map_name = self.game.map.lower()
        for pl in self.players():
            if pl.team != "spectator":
                if str(pl.steam_id) in self.kspree and self.kspree[str(pl.steam_id)] >= 5:
                    if self.kspree[str(pl.steam_id)] > self.record:
                        self.db.zadd(SPREE_KEY.format(map_name), self.kspree[str(pl.steam_id)], "{},{}".format(pl.steam_id, int(time.time())))
                        msg = "{}'s killing spree ended (^1{} ^7kills) by end of game.".format(pl.name, self.kspree[str(pl.steam_id)])
                        self.msg(msg)
                        self.msg("This is a new map record!")
                    else:
                        msg = "{}'s killing spree ended (^1{} ^7kills) by end of game.".format(pl.name, self.kspree[str(pl.steam_id)])
                        self.msg(msg)
        self.kspree.clear()

    def handle_round_end(self, data):
        map_name = self.game.map.lower()
        for pl in self.players():
            if pl.team != "spectator":
                if str(pl.steam_id) in self.kspree and self.kspree[str(pl.steam_id)] >= 5:
                    if self.kspree[str(pl.steam_id)] > self.record:
                        self.db.zadd(SPREE_KEY.format(map_name), self.kspree[str(pl.steam_id)], "{},{}".format(pl.steam_id, int(time.time())))
                        msg = "{}'s killing spree ended (^1{} ^7kills) by end of round.".format(pl.name, self.kspree[str(pl.steam_id)])
                        self.msg(msg)
                        self.msg("This is a new map record!")
                    else:
                        msg = "{}'s killing spree ended (^1{} ^7kills) by end of round.".format(pl.name, self.kspree[str(pl.steam_id)])
                        self.msg(msg)
        self.kspree.clear()

    def handle_map(self, map_name, factory):
        if self.db.zrevrange(SPREE_KEY.format(map_name), 0, 0, withscores=True):
            self.record = int(self.db.zrevrange(SPREE_KEY.format(map_name), 0, 0, withscores=True)[0][1])
        else:
            self.record = 0

    def cmd_spree_record(self, player, msg, channel):
        map_name = self.game.map.lower()
        if self.db.zrevrange(SPREE_KEY.format(map_name), 0, 0, withscores=True):
            spree = self.db.zrevrange(SPREE_KEY.format(map_name), 0, 0, withscores=True)
            spree_record = int(spree[0][1])
            steam_id = spree[0][0].split(",")
            name = self.db.lindex("minqlx:players:{}".format(steam_id[0]), 0)
            if not name:
                msg = "Killing spree record for map '{}': ^1{} ^7kills by BOT.".format(map_name, spree_record)
                self.msg(msg)
            else:
                msg = "Killing spree record for map '{}': ^1{} ^7kills by {}.".format(map_name, spree_record, name)
                self.msg(msg)
        else:
            self.msg("There is no killing spree record for map '" + map_name + "' yet.")

    def cmd_clear_spree_record(self, player, msg, channel):
        map_name = self.game.map.lower()
        del self.db[SPREE_KEY.format(map_name)]
        self.record = 0
        channel.reply("Killing spree record for map '{}' was cleared.".format(map_name))

    def cmd_multikills(self, player, msg, channel):
        if self.db.lrange(PLAYER_KEY.format(player.steam_id) + ":multikills", 0, -1):
            multikills = self.db.lrange(PLAYER_KEY.format(player.steam_id) + ":multikills", 0, -1)
            self.msg(player.name + " has made: " + multikills[0][0] + " multi, " + multikills[1][0] + " mega, " + multikills[2][0] + " ultra, "
                     + multikills[3][0] + " monster, " + multikills[4][0] + " ludicrous, " + multikills[5][0] + " holy shit kills.")
        else:
            self.msg(player.name + " has made no multikills yet.")
