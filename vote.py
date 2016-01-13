# Created by x0rnn and Thomas 'tjone270' Jones (thomas@tomtecsolutions.com)
# vote.py, a plugin to call the following custom votes:
# mode <vql/pql>: change between VQL/Classic and PQL/Turbo mode without the use of custom factories
# weaponrespawn <5/10/15>: set weapon respawn time in seconds (5 is only allowed in VQL mode), 10 is default in PQL
# thrufloors <on/off>: set damage through floors on or off (default)
# footsteps <on/off>: set footsteps on or off (cannot be changed in PQL)
# overtime <0/120>: set overtime to 0 (sudden death) or 120 seconds (default)
# lgdamage <6/7>: set LG damage to either 6 (QL nerf) or 7 (QL pre-nerf) and knockback to 1.75 and 1.50 accordingly
# mgdamage <5/7>: set MG damage to either 5 (QL default) or 7 (Q3 default)
# rgdamage <80/100>: set RG damage to either 80 (QL default) or 100 (Q3 default)
# rlvelocity <900/1000>: set RL velocity to either 900 (Q3 default) or 1000 (QL default)
# reset <vql/pql>: reset all custom votes to default VQL/PQL settings
# spec <id>: move a player to spectators
# mute <id>: mute a player for 10 minutes
# midair <on/off>: enable or disable rockets-only midair mode
# rocketinstagib <on/off>: enable or disable rocket instagib for midair mode
# instagib <on/off>: enable or disable railgun instagib mode
# crouchslide <on/off>: enable or disable crouchslide (Q4) mode
# note that the plugin is tailored for duel gameplay, voting/resetting to VQL/PQL changes starting weapons to gauntlet + MG which can be a problem if you have loadouts enabled or are running a factory where you spawn with other weapons by default

import minqlx

class vote(minqlx.Plugin):
    def __init__(self):
        self.add_hook("vote_called", self.handle_vote_called)
        self.add_hook("player_loaded", self.player_loaded)
        self.add_command("votemenu", self.cmd_votemenu)

    def cmd_votemenu(self, player, msg, channel):
        player.tell("^3Use /cv or /callvote to vote for the following:\n"
                    "^5mode <vql/pql>           ^3- ^7change between VQL/PQL\n"
                    "^5weaponrespawn <5/10/15>  ^3- ^7set weapon respawn time in seconds (5 is only allowed in VQL mode)\n"
                    "^5thrufloors <on/off>      ^3- ^7set damage through floors on or off (default)\n"
                    "^5footsteps <on/off>       ^3- ^7set footsteps on or off (cannot be changed in PQL)\n"
                    "^5overtime <0/120>         ^3- ^7set overtime to 0 (sudden death) or 120 seconds (default)\n"
                    "^5lgdamage <6/7>           ^3- ^7set LG damage to either 6 or 7 (and knockback to 1.75 or 1.50)\n"
                    "^5mgdamage <5/7>           ^3- ^7set MG damage to either 5 (QL default) or 7 (Q3 default)\n"
                    "^5rgdamage <80/100>        ^3- ^7set RG damage to either 80 (QL default) or 100 (Q3 default)\n"
                    "^5rlvelocity <900/1000>    ^3- ^7set RL velocity to either 900 (Q3 default) or 1000 (QL default)\n"
                    "^5reset <vql/pql>          ^3- ^7reset all custom votes to default VQL/PQL settings\n"
                    "^5spec <id>                ^3- ^7move a player to spectators\n"
                    "^5mute <id>                ^3- ^7mute a player for 10 minutes\n"
                    "^5midair <on/off>          ^3- ^7enable or disable rockets-only midair mode\n"
                    "^5rocketinstagib <on/off>  ^3- ^7enable or disable rocket instagib for midair mode\n"
                    "^5instagib <on/off>        ^3- ^7enable or disable railgun instagib mode\n"
                    "^5crouchslide <on/off>     ^3- ^7enable or disable crouchslide (Q4) mode")
        return minqlx.RET_STOP_ALL

    def player_loaded(self, player):
        if self.get_cvar("pmove_AirControl", bool):
            player.tell("PQL/Turbo is ^2enabled^7. To change, ^2/cv mode vql^7.")
        if self.get_cvar("g_weaponRespawn" == "10") and not self.get_cvar("pmove_AirControl", bool):
            player.tell("Weapon respawn is set to ^210 seconds^7 (not default). To change, ^2/cv weaponrespawn^7.")
        if self.get_cvar("g_weaponRespawn") == "15":
            player.tell("Weapon respawn is set to ^215 seconds^7 (not default). To change, ^2/cv weaponrespawn^7.")
        if self.get_cvar("g_forceDmgThroughSurface", bool):
            player.tell("Damage through floors is ^2enabled^7 (not default). To disable, ^2/cv thrufloors off^7.")
        if self.get_cvar("g_overtime") == "0":
            player.tell("Sudden death is ^2enabled^7 (not default). To disable, ^2/cv overtime 120^7.")
        if self.get_cvar("g_damage_lg") == "7":
            player.tell("LG damage is set to ^27^7 (not default). To change, ^2/cv lgdamage 6^7.")
        if self.get_cvar("g_damage_mg") == "7":
            player.tell("MG damage is set to ^27^7 (not default). To change, ^2/cv mgdamage 5^7.")
        if self.get_cvar("g_damage_rg") == "100":
            player.tell("RG damage is set to ^2100^7 (not default). To change, ^2/cv rgdamage 80^7.")
        if self.get_cvar("g_velocity_rl") == "900":
            player.tell("RL velocity is set to ^2900^7 (not default). To change, ^2/cv rlvelocity 1000^7.")
        if self.get_cvar("g_instaGib", bool):
            player.tell("Instagib is ^2enabled^7 (not default). To disable, ^2/cv instagib off^7.")
        if self.get_cvar("pmove_CrouchSlide", bool):
            player.tell("Crouchslide is ^2enabled^7 (not default). To disable, ^2/cv crouchslide off^7.")
        if self.get_cvar("dmflags") == "32" and not self.get_cvar("pmove_AirControl", bool):
            player.tell("Footsteps are ^2off^7 (not default). To enable, ^2/cv footsteps on^7.")
        if self.get_cvar("g_startingArmor") == "999":
            player.tell("Rockets-only midair mode is ^2on^7 (not default). To disable, ^2/cv midair off^7.")
        if self.get_cvar("g_damage_rl") == "2000":
            player.tell("Rocket instagib is ^2on^7 (not default). To disable, ^2/cv rocketinstagib off^7.")

    def handle_vote_called(self, caller, vote, args):
        if not self.get_cvar("g_allowSpecVote", bool) and caller.team == "spectator":
            caller.tell("You are not allowed to call a vote as spectator.")
            return

        if vote.lower() == "mode":
            if args.lower() == "pql": #pql here uses CPMA values for plasmagun: 18 dmg, 20 splashradius, 100% knockback, and not as outlined on: http://www.syncerror.com/wiki/index.php/Quake_Live:PQL
                self.callvote("dmflags 32;g_damage_pg 18;g_knockback_g 0.5;g_knockback_pg 1;g_knockback_rl 1.10;g_knockback_z 40;g_max_knockback 160;"
                              "g_velocity_gl 800;g_respawn_delay_max 3500;g_respawn_delay_min 500;"
                              "g_startingHealthBonus 0;g_startingAmmo_mg 50;g_weaponRespawn 10;weapon_reload_rg 1250;weapon_reload_sg 950;"
                              "armor_tiered 1;pmove_AirControl 1;pmove_RampJump 1;pmove_ChainJump 1;"
                              "pmove_CircleStrafeFriction 6.0f;pmove_CrouchStepJump 1;pmove_WaterSwimScale 0.6f;"
                              "pmove_WaterWadeScale 0.8f;pmove_WeaponDropTime 10;pmove_WeaponRaiseTime 10;pmove_CrouchSlide 0;"
                              "g_startingArmor 0;g_splashdamage_rl 84;g_damage_rl 100;g_infiniteAmmo 0;g_spawnItemPowerup 1;"
                              "g_spawnItemAmmo 1;g_spawnItemArmor 1;g_spawnItemHoldable 1;g_spawnItemHealth 1;g_spawnItemWeapons 1;"
                              "map_restart", "Enable PQL/Turbo mode?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args.lower() == "vql":
                self.callvote("dmflags 0;g_damage_pg 20;g_knockback_g 1;g_knockback_pg 1.10;g_knockback_rl 0.90;g_knockback_z 24;g_max_knockback 120;"
                              "g_velocity_gl 700;g_respawn_delay_max 2100;g_respawn_delay_min 2400;"
                              "g_startingHealthBonus 25;g_startingAmmo_mg 100;g_weaponRespawn 5;weapon_reload_rg 1500;weapon_reload_sg 1000;"
                              "armor_tiered 0;pmove_AirControl 0;pmove_RampJump 0;pmove_ChainJump 1;"
                              "pmove_CircleStrafeFriction 6.0f;pmove_CrouchStepJump 0;pmove_WaterSwimScale 0.5f;"
                              "pmove_WaterWadeScale 0.75f;pmove_WeaponDropTime 200;pmove_WeaponRaiseTime 200;pmove_CrouchSlide 0;"
                              "g_startingArmor 0;g_splashdamage_rl 84;g_damage_rl 100;g_infiniteAmmo 0;g_spawnItemPowerup 1;"
                              "g_spawnItemAmmo 1;g_spawnItemArmor 1;g_spawnItemHoldable 1;g_spawnItemHealth 1;g_spawnItemWeapons 1;"
                              "map_restart", "Enable VQL/Classic mode?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL

            else:
                caller.tell("^2/cv mode [vql/pql]^7 is the usage for this callvote command.")
                return minqlx.RET_STOP_ALL

        if vote.lower() == "weaponrespawn":
            if args == "5" and self.get_cvar("pmove_AirControl", bool):
                player.tell("In PQL, you can only vote 10 or 15 seconds.")
                return minqlx.RET_STOP_ALL
            elif args == "5" and not self.get_cvar("pmove_AirControl", bool):
                self.callvote("g_weaponRespawn 5", "Set weapon respawn to 5 seconds?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args == "10":
                self.callvote("g_weaponRespawn 10", "Set weapon respawn to 10 seconds?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args == "15":
                self.callvote("g_weaponRespawn 15", "Set weapon respawn to 15 seconds?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            else:
                caller.tell("^2/cv weaponrespawn [5/10/15]^7 is the usage for this callvote command.")
                return minqlx.RET_STOP_ALL

        if vote.lower() == "thrufloors":
            if args.lower() == "off":
                self.callvote("g_forceDmgThroughSurface 0", "Turn off damage through floors?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args.lower() == "on":
                self.callvote("g_forceDmgThroughSurface 1", "Turn on damage through floors?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            else:
                caller.tell("^2/cv thrufloors [on/off]^7 is the usage for this callvote command.")
                return minqlx.RET_STOP_ALL

        if vote.lower() == "overtime":
            if args == "0":
                self.callvote("g_overtime 0", "Enable sudden death?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args == "120":
                self.callvote("g_overtime 120", "Enable 2 minute overtime?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            else:
                caller.tell("^2/cv overtime [0/120]^7 is the usage for this callvote command.")
                return minqlx.RET_STOP_ALL

        if vote.lower() == "lgdamage":
            if args == "6":
                self.callvote("g_damage_lg 6;g_knockback_lg 1.75", "Set LG damage to 6 (default)?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args == "7":
                self.callvote("g_damage_lg 7;g_knockback_lg 1.50", "Set LG damage to 7?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            else:
                caller.tell("^2/cv lgdamage [6/7]^7 is the usage for this callvote command.")
                return minqlx.RET_STOP_ALL

        if vote.lower() == "rgdamage":
            if args == "80":
                self.callvote("g_damage_rg 80", "Set RG damage to 80 (default)?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args == "100":
                self.callvote("g_damage_rg 100", "Set RG damage to 100?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            else:
                caller.tell("^2/cv rgdamage [80/100]^7 is the usage for this callvote command.")
                return minqlx.RET_STOP_ALL

        if vote.lower() == "mgdamage":
            if args == "5":
                self.callvote("g_damage_mg 5", "Set MG damage to 5 (default)?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args == "7":
                self.callvote("g_damage_mg 7", "Set MG damage to 7?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            else:
                caller.tell("^2/cv mgdamage [5/7]^7 is the usage for this callvote command.")
                return minqlx.RET_STOP_ALL

        if vote.lower() == "rlvelocity":
            if args == "900":
                self.callvote("g_velocity_rl 900", "Set RL velocity to 900 (Q3 default)?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args == "1000":
                self.callvote("g_velocity_rl 1000", "Set RL velocity to 1000 (QL default)?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            else:
                caller.tell("^2/cv rlvelocity [900/1000]^7 is the usage for this callvote command.")
                return minqlx.RET_STOP_ALL

        if vote.lower() == "reset":
            if args.lower() == "pql":
                self.callvote("dmflags 32;g_damage_pg 18;g_startingWeapons 3;g_startingAmmo_mg 50;g_knockback_g 0.5;g_knockback_pg 1;g_knockback_rl 1.10;g_knockback_z 40;g_max_knockback 160;g_velocity_gl 800;g_respawn_delay_max 3500;g_respawn_delay_min 500;g_startingHealthBonus 0;g_weaponRespawn 10;weapon_reload_rg 1250;weapon_reload_sg 950;armor_tiered 1;pmove_AirControl 1;pmove_RampJump 1;pmove_ChainJump 1;pmove_CircleStrafeFriction 6.0f;pmove_CrouchStepJump 1;pmove_WaterSwimScale 0.6f;pmove_WaterWadeScale 0.8f;pmove_WeaponDropTime 10;pmove_WeaponRaiseTime 10;g_forceDmgThroughSurface 0;g_overtime 120;g_damage_lg 6;g_knockback_lg 1.75;g_damage_mg 5;g_damage_rg 80;g_velocity_rl 1000;g_instaGib 0;pmove_CrouchSlide 0;g_startingArmor 0;g_splashdamage_rl 84;g_damage_rl 100;g_infiniteAmmo 0;g_spawnItemPowerup 1;g_spawnItemAmmo 1;g_spawnItemArmor 1;g_spawnItemHoldable 1;g_spawnItemHealth 1;g_spawnItemWeapons 1;map_restart", "Reset to default PQL settings?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args.lower() == "vql":
                self.callvote("dmflags 0;g_damage_pg 20;g_startingWeapons 3;g_startingAmmo_mg 100;g_knockback_g 1;g_knockback_pg 1.10;g_knockback_rl 0.90;g_knockback_z 24;g_max_knockback 120;g_velocity_gl 700;g_respawn_delay_max 2100;g_respawn_delay_min 2400;g_startingHealthBonus 25;g_weaponRespawn 5;weapon_reload_rg 1500;weapon_reload_sg 1000;armor_tiered 0;pmove_AirControl 0;pmove_RampJump 0;pmove_ChainJump 1;pmove_CircleStrafeFriction 6.0f;pmove_CrouchStepJump 0;pmove_WaterSwimScale 0.5f;pmove_WaterWadeScale 0.75f;pmove_WeaponDropTime 200;pmove_WeaponRaiseTime 200;g_forceDmgThroughSurface 0;g_overtime 120;g_damage_lg 6;g_knockback_lg 1.75;g_damage_mg 5;g_damage_rg 80;g_velocity_rl 1000;g_instaGib 0;pmove_CrouchSlide 0;g_startingArmor 0;g_splashdamage_rl 84;g_damage_rl 100;g_infiniteAmmo 0;g_spawnItemPowerup 1;g_spawnItemAmmo 1;g_spawnItemArmor 1;g_spawnItemHoldable 1;g_spawnItemHealth 1;g_spawnItemWeapons 1;map_restart", "Reset to default VQL settings?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            else:
                caller.tell("^2/cv reset [vql/pql]^7 is the usage for this callvote command.")
                return minqlx.RET_STOP_ALL

        if vote.lower() == "spec":
            try:
                player_name = self.player(int(args)).clean_name
                player_id = self.player(int(args)).id
            except:
                caller.tell("^1Invalid ID.^7 Use a client ID from the ^2/players^7 command.")
                return minqlx.RET_STOP_ALL

            if self.player(int(args)).team == "spectator":
                caller.tell("That player is already in the spectators.")
                return minqlx.RET_STOP_ALL
            
            self.callvote("put {} spec".format(player_id), "Move {} to the spectators?".format(player_name))
            self.msg("{}^7 called a vote.".format(caller.name))
            return minqlx.RET_STOP_ALL

        if vote.lower() == ("mute"):
            try:
                player_name = self.player(int(args)).clean_name
                player_id = self.player(int(args)).id
            except:
                caller.tell("^1Invalid ID.^7 Use a client ID from the ^2/players^7 command.")
                return minqlx.RET_STOP_ALL
            
            self.callvote("qlx !silence {} 10 minutes You were call-voted silent for 10 minutes.;mute {}".format(player_id, player_id), "Mute {} for 10 minutes?".format(player_name))
            self.msg("{}^7 called a vote.".format(caller.name))
            return minqlx.RET_STOP_ALL

        if vote.lower() == "instagib":
            if args.lower() == "on":
                self.callvote("g_instaGib 1;g_startingWeapons 65;g_spawnItemPowerup 0;g_spawnItemAmmo 0;g_spawnItemArmor 0;g_spawnItemHoldable 0;g_spawnItemHealth 0;g_spawnItemWeapons 0;map_restart", "Enable railgun instagib mode?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args.lower() == "off":
                self.callvote("g_instaGib 0;g_startingWeapons 3;g_spawnItemPowerup 1;g_spawnItemAmmo 1;g_spawnItemArmor 1;g_spawnItemHoldable 1;g_spawnItemHealth 1;g_spawnItemWeapons 1;map_restart", "Disable railgun instagib mode?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            else:
                caller.tell("^2/cv instagib [on/off]^7 is the usage for this callvote command.")
                return minqlx.RET_STOP_ALL

        if vote.lower() == "crouchslide":
            if args.lower() == "on" and self.get_cvar("pmove_AirControl", bool):
                caller.tell("^7Crouchslide can only be voted in VQL mode, please do ^2/cv mode vql^7 first.")
                return minqlx.RET_STOP_ALL
            elif args.lower() == "on" and not self.get_cvar("pmove_AirControl", bool):
                self.callvote("pmove_CrouchSlide 1;pmove_CrouchSlideTime 1000;pmove_RampJump 1;pmove_CrouchStepJump 1;map_restart", "Enable crouchslide mode?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args.lower() == "off" and self.get_cvar("pmove_CrouchSlide", bool):
                self.callvote("pmove_CrouchSlide 0;pmove_RampJump 0;pmove_CrouchStepJump 0;map_restart", "Disable crouchslide mode?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args.lower() == "off" and not self.get_cvar("pmove_CrouchSlide", bool):
                caller.tell("^7Crouchslide is already off.")
                return minqlx.RET_STOP_ALL
            else:
                caller.tell("^2/cv crouchslide [on/off]^7 is the usage for this callvote command.")
                return minqlx.RET_STOP_ALL

        if vote.lower() == "footsteps":
            if args.lower() == "on" and self.get_cvar("pmove_AirControl", bool):
                caller.tell("^7Footsteps can only be enabled in VQL mode.")
                return minqlx.RET_STOP_ALL
            elif args.lower() == "on" and not self.get_cvar("pmove_AirControl", bool):
                self.callvote("dmflags 0", "Enable footsteps?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args.lower() == "off" and self.get_cvar("pmove_AirControl", bool):
                caller.tell("^7Footsteps are already off.")
                return minqlx.RET_STOP_ALL
            elif args.lower() == "off" and not self.get_cvar("pmove_AirControl", bool):
                self.callvote("dmflags 32", "Disable footsteps?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            else:
                caller.tell("^2/cv footsteps [on/off]^7 is the usage for this callvote command.")
                return minqlx.RET_STOP_ALL

        if vote.lower() == "midair":
            if args.lower() == "on" and self.get_cvar("pmove_AirControl", bool):
                caller.tell("^7Midair mode can only be voted in VQL mode, please do ^2/cv mode vql^7 first.")
                return minqlx.RET_STOP_ALL
            elif args.lower() == "on" and not self.get_cvar("pmove_AirControl", bool):
                self.callvote("dmflags 16;g_startingWeapons 16;g_startingArmor 999;g_startingHealthBonus 0;g_splashdamage_rl 0;g_damage_rl 150;g_knockback_rl 1.80;g_knockback_z 700;g_infiniteAmmo 1;g_spawnItemPowerup 0;g_spawnItemAmmo 0;g_spawnItemArmor 0;g_spawnItemHoldable 0;g_spawnItemHealth 0;g_spawnItemWeapons 0;map_restart", "Enable rockets-only midair mode?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args.lower() == "off" and self.get_cvar("pmove_AirControl", bool):
                caller.tell("^7Midair is already off.")
                return minqlx.RET_STOP_ALL
            elif args.lower() == "off" and not self.get_cvar("pmove_AirControl", bool):
                self.callvote("dmflags 0;g_startingWeapons 3;g_startingArmor 0;g_startingHealthBonus 25;g_splashdamage_rl 84;g_damage_rl 100;g_knockback_rl 0.90;g_knockback_z 24;g_infiniteAmmo 0;g_spawnItemPowerup 1;g_spawnItemAmmo 1;g_spawnItemArmor 1;g_spawnItemHoldable 1;g_spawnItemHealth 1;g_spawnItemWeapons 1;map_restart", "Disable rockets-only midair mode?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            else:
                caller.tell("^2/cv midair [on/off]^7 is the usage for this callvote command.")
                return minqlx.RET_STOP_ALL

        if vote.lower() == "rocketinstagib":
            if args.lower() == "on" and self.get_cvar("g_startingArmor") == "0":
                caller.tell("^7Rocket instagib can only be voted in midair mode, please do ^2/cv midair on^7 first.")
                return minqlx.RET_STOP_ALL
            elif args.lower() == "on" and self.get_cvar("g_startingArmor") == "999":
                self.callvote("g_damage_rl 2000", "Enable rocket instagib?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            elif args.lower() == "off" and self.get_cvar("g_startingArmor") == "0":
                caller.tell("^7Rocket instagib is already off.")
                return minqlx.RET_STOP_ALL
            elif args.lower() == "off" and self.get_cvar("g_startingArmor") == "999":
                self.callvote("g_damage_rl 150", "Disable rocket instagib?")
                self.msg("{}^7 called a vote.".format(caller.name))
                return minqlx.RET_STOP_ALL
            else:
                caller.tell("^2/cv rocketinstagib [on/off]^7 is the usage for this callvote command.")
                return minqlx.RET_STOP_ALL
