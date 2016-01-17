# midair_only.py, this plugin changes the gameplay into a rockets-only mode where only midair shots kill.
# If you just want a midair ranking system, use midair.py instead.
# This plugin also keeps score of top X midair rocket kills per map in terms of distance.
# On evey midair kill that counts (minheight and mindistance variables), a text message will inform everyone
# about the distance involved, and who killed who, together with a "Holy shit" sound announcement.
# If the map record has been broken, then the "New high score" announcement will be used instead.
# Also shows a kill counter of Killer:Victim (taken from pummel.py by mattiZed).
# !top will list top X map records, !mytop will list your top X map records.
# !kills/!killstats will list top X players with most midair kills and their kill count for the current map.
# (admins only) !cleartopshots will clear all map topshots, !clearkillstats will clear all map killstats.
# by x0rnn, mattiZed, kanzo, iou; thanks guys :)

import minqlx
import minqlx.database
import math
import time

MIDAIR_KEY = "minqlx:midair:{}"
PLAYER_KEY = "minqlx:players:{}"

class midair_only(minqlx.Plugin):
    def __init__(self):
        self.add_hook("frame", self.handle_frame, priority=minqlx.PRI_LOWEST)
        self.add_hook("death", self.handle_death)
        self.add_hook("map", self.handle_map)
        self.add_command(("topshots", "top"), self.cmd_topshots)
        self.add_command(("mytopshots", "mytop"), self.cmd_mytopshots)
        self.add_command(("kills", "killstats"), self.cmd_killstats)
        self.add_command("cleartopshots", self.cmd_cleartopshots, 5)
        self.add_command("clearkillstats", self.cmd_clearkillstats, 5)

        self.record = 0.0

    def handle_frame(self):
        for pl in self.players():
            if pl.team != "spectator":
                if pl.health > 0:
                    if pl.velocity().z == 0.0:
                        pl.health = 6666
                    else:
                        pl.health = 100

    def handle_death(self, victim, killer, data):
        if data['KILLER'] is not None:
            if data['KILLER']['WEAPON'] == "ROCKET" and data['VICTIM']['AIRBORNE']:
                k_X = data['KILLER']['POSITION']['X']
                k_Y = data['KILLER']['POSITION']['Y']
                k_Z = data['KILLER']['POSITION']['Z']
                v_X = data['VICTIM']['POSITION']['X']
                v_Y = data['VICTIM']['POSITION']['Y']
                v_Z = data['VICTIM']['POSITION']['Z']
                k_id = data['KILLER']['STEAM_ID']
                v_id = data['VICTIM']['STEAM_ID']
                distance = math.sqrt((v_X - k_X) ** 2 + (v_Y - k_Y) ** 2 + (v_Z - k_Z) ** 2)
                height = abs(data['KILLER']['POSITION']['Z'] - data['VICTIM']['POSITION']['Z'])
                killer_name = data['KILLER']['NAME']
                victim_name = data['VICTIM']['NAME']
                map_name = self.game.map.lower()
                minheight = 100 #min height difference to register midairs
                mindistance = 300 #min length distance to register midairs
                if height > minheight and distance > mindistance:
                    self.db.zadd(MIDAIR_KEY.format(map_name), distance, "{},{},{}".format(k_id, v_id, int(time.time())))
                    self.db.zincrby(MIDAIR_KEY.format(map_name) + ":count", k_id, 1)
                    self.db.zadd(PLAYER_KEY.format(k_id) + ":midair:" + str(map_name), distance, "{},{}".format(v_id, int(time.time())))
                    self.db.sadd(PLAYER_KEY.format(k_id) + ":midair", v_id)
                    self.db.incr(PLAYER_KEY.format(k_id) + ":midair:" + v_id)
                    killer_score = self.db[PLAYER_KEY.format(k_id) + ":midair:" + v_id]
                    victim_score = 0
                    if PLAYER_KEY.format(v_id) + ":midair:" + k_id in self.db:
                        victim_score = self.db[PLAYER_KEY.format(v_id) + ":midair:" + k_id]
                    if distance <= self.record:
                        msg = "{} killed {} from a distance of: ^1{} ^7units. Score: ^2{}^7:^2{}".format(killer_name, victim_name, round(distance), killer_score, victim_score)
                        self.play_sound("sound/vo_evil/holy_shit")
                        self.msg(msg)
                    elif distance > self.record:
                        msg = "^1New map record^7! {} killed {} from a distance of: ^1{} ^7units. Score: ^2{}^7:^2{}".format(killer_name, victim_name, round(distance), killer_score, victim_score)
                        self.play_sound("sound/vo_evil/new_high_score")
                        self.msg(msg)
                        self.record = distance

    def cmd_topshots(self, player, msg, channel):
        x = 5 #how many topshots to list
        map_name = self.game.map.lower()
        topshots = self.db.zrevrange(MIDAIR_KEY.format(map_name), 0, x-1, withscores=True)
        player.tell("^1Midair ^7topshots for map ^1" + map_name + "^7:\n")
        i = 1
        for shot, distance in topshots:
            k_id, v_id, timestamp = map(lambda el: int(el), shot.split(","))
            k_id_name = self.db.lindex(PLAYER_KEY.format(k_id), 0)
            v_id_name = self.db.lindex(PLAYER_KEY.format(v_id), 0)
            if not k_id_name:
                player.tell("^2" + str(i) + "^7: BOT killed {} from a distance of: ^1{} ^7units.".format(v_id_name, round(distance)))
            elif not v_id_name:
                player.tell("^2" + str(i) + "^7: {} killed BOT from a distance of: ^1{} ^7units.".format(k_id_name, round(distance)))
            else:
                player.tell("^2" + str(i) + "^7: {} killed {} from a distance of: ^1{} ^7units.".format(k_id_name, v_id_name, round(distance)))
            i += 1

    def cmd_mytopshots(self, player, msg, channel):
        x = 10 #how many topshots to list
        map_name = self.game.map.lower()
        topshots = self.db.zrevrange(PLAYER_KEY.format(player.steam_id) + ":midair:" + str(map_name), 0, x-1, withscores=True)
        player.tell("^7Your ^1midair ^7topshots for map ^1" + map_name + "^7:\n")
        i = 1
        for shot, distance in topshots:
            v_id, timestamp = map(lambda el: int(el), shot.split(","))
            v_id_name = self.db.lindex(PLAYER_KEY.format(v_id), 0)
            if not v_id_name:
                player.tell("^2" + str(i) + "^7: Victim: BOT, distance: ^1{} ^7units.".format(round(distance)))
            else:
                player.tell("^2" + str(i) + "^7: Victim: {}, distance: ^1{} ^7units.".format(v_id_name, round(distance)))
            i += 1

    def cmd_killstats(self, player, msg, channel):
        x = 5 #how many to list
        map_name = self.game.map.lower()
        killstats = self.db.zrevrange(MIDAIR_KEY.format(map_name) + ":count", 0, x-1, withscores=True)
        player.tell("^7Most midair kills for map ^1" + map_name + "^7:\n")
        i = 1
        for steamid, count in killstats:
            name = self.db.lindex(PLAYER_KEY.format(steamid), 0)
            if not name:
                player.tell("^2" + str(i) + "^7: BOT: ^1{} ^7kills.".format(int(count)))
            else:
                player.tell("^2" + str(i) + "^7: {}^7: ^1{} ^7kills.".format(name, int(count)))
            i += 1

    def cmd_cleartopshots(self, player, msg, channel):
        map_name = self.game.map.lower()
        del self.db[MIDAIR_KEY.format(map_name)]
        self.record = 0.0
        channel.reply("Topshots for map ^1{} ^7were cleared.".format(map_name))

    def cmd_clearkillstats(self, player, msg, channel):
        map_name = self.game.map.lower()
        del self.db[MIDAIR_KEY.format(map_name) + ":count"]
        channel.reply("Killstats for map ^1{} ^7were cleared.".format(map_name))

    def handle_map(self, map_name, factory):
        if self.db.zrevrange(MIDAIR_KEY.format(map_name), 0, 0, withscores=True):
            self.record = self.db.zrevrange(MIDAIR_KEY.format(map_name), 0, 0, withscores=True)[0][1]
        else:
            self.record = 0.0

        self.set_cvar("dmflags", "16")
        self.set_cvar("g_startingWeapons", "16")
        self.set_cvar("g_startingHealthBonus", "0")
        self.set_cvar("g_splashdamage_rl", "0")
        self.set_cvar("g_damage_rl", "1000")
        self.set_cvar("g_knockback_rl", "1.80")
        self.set_cvar("g_knockback_z", "700")
        self.set_cvar("g_infiniteAmmo", "1")
        self.set_cvar("g_spawnItemPowerup", "0")
        self.set_cvar("g_spawnItemAmmo", "0")
        self.set_cvar("g_spawnItemArmor", "0")
        self.set_cvar("g_spawnItemHoldable", "0")
        self.set_cvar("g_spawnItemHealth", "0")
        self.set_cvar("g_spawnItemWeapons", "0")
        self.set_cvar("pmove_BunnyHop", "0")
