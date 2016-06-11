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
# 	3 kills in 4 second intervals: multikill
# 	4 kills in 4 second intervals: mega kill
# 	5 kills in 4 second intervals: ultra kill
# 	6 kills in 4 second intervals: monster kill
# 	7 kills in 4 second intervals: ludicrous kill
# 	8 kills in 4 second intervals: holy shit
#
# !spree_record will print the current map's killing spree record and the player's name
# !clear_spree_record will clear the current map record (admins only)
#
# Selfkilling, switching teams, getting teamkilled or getting killed by the world (lava, falling, etc.)
# will nullify your killing streak and it won't register as a record either.
#
# Use with: https://steamcommunity.com/sharedfiles/filedetails/?id=701783942
# Add 701783942 to qlx_workshopReferences

import minqlx
import time
from collections import defaultdict

SPREE_KEY = "minqlx:spree:{}"
PLAYER_KEY = "minqlx:players:{}"

class killingspree(minqlx.Plugin):
    def __init__(self):
        self.add_hook("death", self.handle_death)
        self.add_hook("game_end", self.handle_game_end)
        self.add_hook("round_end", self.handle_round_end)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("player_loaded", self.player_loaded)
        self.add_hook("map", self.handle_map)
        self.add_command("spree_record", self.cmd_spree_record)
        self.add_command("clear_spree_record", self.cmd_clear_spree_record, 5)

        self.kspree = {}
        self.record = 0
        self.multikill = defaultdict(dict)

    def player_loaded(self, player):
        self.multikill[str(player.steam_id)][0] = 0
        self.multikill[str(player.steam_id)][1] = 0

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

            def checkKSpreeEnd(id, v_name, k_name):
                if id in self.kspree and self.kspree[id] >= 5:
                    if self.kspree[id] > self.record:
                        self.db.zadd(SPREE_KEY.format(map_name), self.kspree[id], "{},{}".format(id, int(time.time())))
                        msg = "{}'s killing spree ended (^1{} ^7kills), killed by {}.".format(v_name, self.kspree[id], k_name)
                        self.msg(msg)
                        self.msg("This is a new map record!")
                    else:
                        msg = "{}'s killing spree ended (^1{} ^7kills), killed by {}.".format(v_name, self.kspree[id], k_name)
                        self.msg(msg)

            def checkMultiKill(id, k_name):
                 current_time = time.time()
                 if current_time - self.multikill[id][0] < 4:
                     self.multikill[id][1] = self.multikill[id][1] + 1
                     if self.multikill[id][1] == 3:
                         self.play_sound("sound/misc/multikill.wav")
                         self.msg("!!! ^1Multi kill ^7> " + k_name + " < ^1Multi kill ^7!!!")
                     elif self.multikill[id][1] == 4:
                         self.play_sound("sound/misc/megakill.wav")
                         self.msg("!!! ^1Mega kill ^7> " + k_name + " < ^1Mega kill ^7!!!")
                     elif self.multikill[id][1] == 5:
                         self.play_sound("sound/misc/ultrakill.wav")
                         self.msg("!!! ^1ULTRA KILL ^7> " + k_name + " < ^1ULTRA KILL ^7!!!")
                     elif self.multikill[id][1] == 6:
                         self.play_sound("sound/misc/monsterkill.wav")
                         self.msg("!!! ^1MONSTER KILL ^7> " + k_name + " < ^1MONSTER KILL^7!!!")
                     elif self.multikill[id][1] == 7:
                         self.play_sound("sound/misc/ludicrouskill.wav")
                         self.msg("!!! ^1LUDICROUS KILL ^7> " + k_name + " < ^1LUDICROUS KILL ^7!!!")
                     elif self.multikill[id][1] == 8:
                         self.play_sound("sound/misc/holyshit.wav")
                         self.msg("!!! ^1 H O L Y  S H I T ^7> " + k_name + " < ^1H O L Y  S H I T ^7!!!")
                 else:
                     self.multikill[id][1] = 1
                 self.multikill[id][0] = time.time()

            v_id = data['VICTIM']['STEAM_ID']

            if data['TEAMKILL']:
                self.kspree[v_id] = 0
                self.multikill[v_id][0] = 0
                self.multikill[v_id][1] = 0
            if data['MOD'] == "SUICIDE": #team switch & /kill
                self.kspree[v_id] = 0
                self.multikill[v_id][0] = 0
                self.multikill[v_id][1] = 0
            if data['KILLER'] is None: #world
                self.kspree[v_id] = 0
                self.multikill[v_id][0] = 0
                self.multikill[v_id][1] = 0

            elif data['KILLER'] is not None and not data['TEAMKILL']:
                k_id = data['KILLER']['STEAM_ID']
                k_name = data['KILLER']['NAME']
                v_name = data['VICTIM']['NAME']

                if k_id not in self.kspree:
                    self.kspree[k_id] = 1
                    checkKSpreeEnd(v_id, v_name, k_name)
                    self.kspree[v_id] = 0
                else:
                    self.kspree[k_id] = self.kspree[k_id] + 1
                    checkKSpree(k_id, k_name)
                    checkKSpreeEnd(v_id, v_name, k_name)
                    self.kspree[v_id] = 0
                checkMultiKill(k_id, k_name)
                self.multikill[v_id][0] = 0
                self.multikill[v_id][1] = 0

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

    def handle_player_disconnect(self, player, reason):
        if str(player.steam_id) in self.kspree:
            self.kspree[str(player.steam_id)] = 0

    def handle_map(self, map_name, factory):
        if self.db.zrevrange(SPREE_KEY.format(map_name), 0, 0, withscores=True):
            self.record = self.db.zrevrange(SPREE_KEY.format(map_name), 0, 0, withscores=True)[0][1]
        else:
            self.record = 0

    def cmd_spree_record(self, player, msg, channel):
        map_name = self.game.map.lower()
        if self.db.zrevrange(SPREE_KEY.format(map_name), 0, 0, withscores=True):
            spree = self.db.zrevrange(SPREE_KEY.format(map_name), 0, 0, withscores=True)
            spree_record = int(spree[0][1])
            steam_id = spree[0][0].split(",")
            name = self.db.lindex(PLAYER_KEY.format(steam_id[0]), 0)
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
