# addbot.py, lets a player add a single nightmare bot into the game with either a 0, 60 or 200 millisecond thinktime (smaller is stronger)
# usage:
# !addbot <thinktime>
# !botskill <thinktime>
# server.cfg should have the following cvars set: bot_enable 1, bot_nochat 1, bot_challenge 1
# by Mino

import minqlx

class addbot(minqlx.Plugin):
    def __init__(self):
        self.add_hook("player_connect", self.handle_player_connect)
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_hook("player_loaded", self.player_loaded)
        self.add_command("addbot", self.cmd_addbot, 0, usage="<skill between 0 and 200: 0 is very difficult, 60 is hard, 200 is easier but still not noob-friendly>")
        self.add_command("botskill", self.cmd_botskill, 0, usage="<skill between 0 and 200: 0 is very difficult, 60 is hard, 200 is easier but still not noob-friendly>")

        self.set_cvar_once("qlx_bot", "Xaero")
        self.set_cvar_once("qlx_botSkill", "5")
        self.set_cvar_once("qlx_botName", "^1X^7aero")

        self.expecting_bot = False
        self.current_bot = None

    def handle_player_connect(self, player):
        if self.expecting_bot:
            self.current_bot = player

    def handle_player_disconnect(self, player, reason):
        if player == self.current_bot:
            self.current_bot = None
        if len(self.players()) <= 2 and self.current_bot:
            minqlx.console_command("kick xaero")
            self.current_bot = None

    def player_loaded(self, player):
        if self.current_bot:
            bot_skill = self.get_cvar("bot_thinktime")
            player.tell("^1X^7aero's skill is ^2" + bot_skill +"^7.\nFor reference, ^20 ^7is very difficult, ^260 ^7is hard, and ^2200 ^7is easier but still not noob-friendly.\nTo change, type ^2!botskill^7.")

    def cmd_botskill(self, player, msg, channel):
        if player.team == "spectator":
            return
        elif len(msg) < 2:
            return minqlx.RET_USAGE
            
        try:
            thinktime = int(msg[1])
            if (thinktime < 0 or thinktime > 200):
                raise ValueError
        except ValueError:
            player.tell("Please select a skill between 0 and 200. 0 is very difficult, 60 is hard, 200 is easier but still not noob-friendly")
            return minqlx.RET_STOP_ALL
        self.set_cvar("bot_thinktime", thinktime)
        self.msg("^1X^7aero's skill has been set to: ^2" + str(thinktime))

    def cmd_addbot(self, player, msg, channel):
        if player.team == "spectator":
            player.tell("You can't use this command as a spectator.")
            return minqlx.RET_STOP_ALL
        elif self.current_bot:
            player.tell("The bot is already active.")
            return minqlx.RET_STOP_ALL
        elif len(msg) < 2:
            return minqlx.RET_USAGE
            
        try:
            thinktime = int(msg[1])
            if (thinktime < 0 or thinktime > 200):
                raise ValueError
        except ValueError:
            player.tell("Please select a skill between 0 and 200. 0 is very difficult, 60 is hard, 200 is easier but still not noob-friendly")
            return minqlx.RET_STOP_ALL
        
        self.set_cvar("bot_thinktime", thinktime)
        teams = self.teams()
        team = "b" if len(teams["red"]) > len(teams["blue"]) else "r"
        self.expecting_bot = True
        minqlx.console_command("addbot {} {} 0 {} \"{}\""
            .format(self.get_cvar("qlx_bot"), self.get_cvar("qlx_botSkill"), team, self.get_cvar("qlx_botName")))
        self.expecting_bot = False
        
