# referee.py, gives referee status to a player with the password or one that has been callvoted (if enabled) and enables the following commands:
#########################################################################
# ref help             - Lists all referee commands
# ref allready         - Force all players to be 'ready' and start the match.
# ref abort            - Abandon the current game and return to warmup.
# ref pause            - Pause the current match indefinitely.
# ref unpause          - Unause the current match.
# ref lock [r/b]       - Stop players from joining the team.
# ref unlock [r/b]     - Allow players to join the team.
# ref freecam <0/1>    - Disable/enable freecam spectator mode for dead players.
# ref alltalk <0/1>    - Disable/enable communication between teams.
# ref put <id> [r/b/s] - Move a player to red/blue/spectators.
# ref mute <id>        - Mute a player.
# ref unmute <id>      - Unmute a player.
# ref kick <id>        - Kick a player.
# ref tempban <id>     - Temporarily kickban a player.
#########################################################################
# The commands can be input via the console, for example: /ref allready, or through the chat: !ref allready
# The only exceptions being "/ref pass" and "/ref help", which are console-only.
# "ref kick" and "ref tempban" are disabled by default, set qlx_allowRefKick and qlx_allowRefKickban to 1 to enable them.
# To get referee status, type /ref pass "password" (without quotation marks).
# The initial password is set on line 42 of this file ("CHANGE_ME"), change it to something unique.
# You can change the password in-game/between matches (minqlx admin only) with !setrefpass "password" (without quotation marks), which will also reset all current referees.
# To show the currently set password, type !getrefpass (minqlx admin only); to show a list of referees currently on the server, type !referees.
# Voting for referees is disabled by default, set qlx_allowRefVote to 1 to enable it. If enabled, the vote commands are: /cv referee <id>, /cv unreferee <id>

import minqlx
import re

class referee(minqlx.Plugin):
    def __init__(self):
        self.add_hook("client_command", self.handle_client_command)
        self.add_hook("player_loaded", self.player_loaded)
        self.add_hook("vote_called", self.handle_vote_called)
        self.add_command("setrefpass", self.cmd_setrefpass, 5, usage="<password> (no spaces)")
        self.add_command("getrefpass", self.cmd_getrefpass, 5)
        self.add_command("ref", self.cmd_ref)
        self.add_command("referees", self.cmd_referees)
        self.add_command("votereferee", self.cmd_votereferee, 5, usage="<id>")
        self.add_command("voteunreferee", self.cmd_voteunreferee, 5, usage="<id>")

        self.password = "CHANGE_ME"
        self.referees = []
        self.set_cvar_once("qlx_allowRefVote", "0")
        self.set_cvar_once("qlx_allowRefKick", "0")
        self.set_cvar_once("qlx_allowRefKickban", "0")

    def player_loaded(self, player):
        if self.referees:
            player.tell("^6Referees ^7currently on the server:\n")
            for refs in self.referees:
                for p in self.players():
                    if p.steam_id == refs:
                        player.tell(p.name)

    def cmd_votereferee(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE
        else:
            if self.player(int(msg[1])):
                self.referees.append(self.player(int(msg[1])).steam_id)
                self.msg(self.player(int(msg[1])).name + " has been made a ^6Referee^7.")
                self.player(int(msg[1])).tell("^5/ref help to list all referee commands.")
            else:
                return minqlx.RET_USAGE

    def cmd_voteunreferee(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE
        else:
            if self.player(int(msg[1])):
                self.referees.remove(self.player(int(msg[1])).steam_id)
                self.msg(self.player(int(msg[1])).name + " has been unrefereed.")
            else:
                return minqlx.RET_USAGE

    def handle_vote_called(self, caller, vote, args):
        if not self.get_cvar("qlx_allowRefVote", bool):
            caller.tell("Referee voting has been disabled.")
            return minqlx.RET_STOP_ALL
        elif not (self.get_cvar("g_allowSpecVote", bool)) and caller.team == "spectator":
            caller.tell("You are not allowed to call a vote as a spectator.")
            return minqlx.RET_STOP_ALL
        else:
            if vote.lower() == "referee":
                if (0 <= int(args) < 64):
                    if self.player(int(args)):
                        self.callvote("qlx !votereferee " + args, "^3Set " + self.player(int(args)).name + " ^3as a referee?")
                        self.msg("{}^7 called a vote.".format(caller.name))
                        return minqlx.RET_STOP_ALL
                    else:
                        caller.tell("No player with ID: ^2" + str(args) + "^7 on the server.")
                        return minqlx.RET_STOP_ALL
                else:
                    caller.tell("^2/cv referee <id>^7 is the usage for this callvote command.")
                    return minqlx.RET_STOP_ALL
            elif vote.lower() == "unreferee":
                if (0 <= int(args) < 64):
                    if self.player(int(args)) and self.player(int(args)).steam_id in self.referees:
                        self.callvote("qlx !voteunreferee " + args, "^3Unreferee " + self.player(int(args)).name + " ^3?")
                        self.msg("{}^7 called a vote.".format(caller.name))
                        return minqlx.RET_STOP_ALL
                    elif self.player(int(args)) and self.player(int(args)).steam_id not in self.referees:
                        caller.tell("That player is not a referee.")
                        return minqlx.RET_STOP_ALL
                    else:
                        caller.tell("No player with ID: ^2" + str(args) + "^7 on the server.")
                        return minqlx.RET_STOP_ALL
                else:
                    caller.tell("^2/cv unreferee <id>^7 is the usage for this callvote command.")
                    return minqlx.RET_STOP_ALL

    def handle_client_command(self, caller, cmd):
        if cmd == "ref pass " + self.password:
            self.referees.append(caller.steam_id)
            caller.tell("^5Password correct, referee status granted. /ref help to list all commands.")

        elif cmd.lower() == "ref help" and caller.steam_id in self.referees:
            caller.tell("^3Use /ref or !ref <cmd> [arg]:\n"
                        "^5allready               ^3- ^7Force all players to be 'ready' and start the match.\n"
                        "^5abort                  ^3- ^7Abandon the current game and return to warmup.\n"
                        "^5pause                  ^3- ^7Pause the current match indefinitely.\n"
                        "^5unpause                ^3- ^7Unause the current match.\n"
                        "^5lock <r/b>             ^3- ^7Stop players from joining the team. (both if no arg given)\n"
                        "^5unlock <r/b>           ^3- ^7Allow players to join the team. (both if no arg given)\n"
                        "^5freecam <0/1>          ^3- ^7Disable/enable freecam spectator mode for dead players.\n"
                        "^5alltalk <0/1>          ^3- ^7Disable/enable communication between teams.\n"
                        "^5put <id> [r/b/s]       ^3- ^7Move a player to red/blue/spectators.\n"
                        "^5mute <id>              ^3- ^7Mute a player.\n"
                        "^5unmute <id>            ^3- ^7Unmute a player.\n"
                        "^5kick <id>              ^3- ^7Kick a player.\n"
                        "^5tempban <id>           ^3- ^7Temporarily kickban a player.")

        elif cmd.lower() == "ref allready" and caller.steam_id in self.referees:
            if self.game.state == "warmup":
                self.msg("^6Referee ^7" + str(caller) + " readied the teams.")
                self.allready()
            else:
                caller.tell("The game is already in progress.")

        elif cmd.lower() == "ref abort" and caller.steam_id in self.referees:
            if self.game.state != "warmup":
                self.msg("^6Referee ^7" + str(caller) + " aborted the match.")
                self.abort()
            else:
                caller.tell("The match hasn't started yet.")

        elif cmd.lower() == "ref pause" and caller.steam_id in self.referees:
            if self.game.state != "warmup":
                self.msg("^6Referee ^7" + str(caller) + " paused the match.")
                self.pause()
            else:
                caller.tell("The match hasn't started yet.")

        elif cmd.lower() == "ref unpause" and caller.steam_id in self.referees:
            if self.game.state != "warmup":
                self.msg("^6Referee ^7" + str(caller) + " unpaused the match.")
                self.unpause()
            else:
                caller.tell("The match hasn't started yet.")

        elif cmd.lower() == "ref lock" and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " locked the teams.")
            self.lock()

        elif (cmd.lower() == "ref lock r" or cmd.lower() == "ref lock red") and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " locked the ^1red ^7team.")
            self.lock("red")

        elif (cmd.lower() == "ref lock b" or cmd.lower() == "ref lock blue") and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " locked the ^4blue ^7team.")
            self.lock("blue")

        elif cmd.lower() == "ref unlock" and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " unlocked the teams.")
            self.unlock()

        elif (cmd.lower() == "ref unlock r" or cmd.lower() == "ref unlock red") and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " unlocked the ^1red ^7team.")
            self.unlock("red")

        elif (cmd.lower() == "ref unlock b" or cmd.lower() == "ref unlock blue") and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " unlocked the ^4blue ^7team.")
            self.unlock("blue")

        elif (cmd.lower() == "ref freecam 0" or cmd.lower() == "ref freecam off") and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " disabled freecam spectator mode.")
            self.set_cvar("g_teamSpecFreeCam", "0")

        elif (cmd.lower() == "ref freecam 1" or cmd.lower() == "ref freecam on") and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " enabled freecam spectator mode.")
            self.set_cvar("g_teamSpecFreeCam", "1")

        elif (cmd.lower() == "ref alltalk 0" or cmd.lower() == "ref alltalk off") and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " disabled communication between teams.")
            self.set_cvar("g_allTalk", "0")

        elif (cmd.lower() == "ref alltalk 1" or cmd.lower() == "ref alltalk on") and caller.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(caller) + " enabled communication between teams.")
            self.set_cvar("g_allTalk", "1")

        elif re.search(r"ref put \d+ s", cmd.lower()) and caller.steam_id in self.referees:
            id = re.search(r"\d+", cmd.lower()).group()
            if self.player(int(id)):
                self.msg("^6Referee ^7" + str(caller) + " moved " + self.player(int(id)).name + " to the spectators.")
                self.player(int(id)).put("spectator")
            else:
                caller.tell("No player with ID: ^2" + id + "^7.")

        elif re.search(r"ref mute \d+", cmd.lower()) and caller.steam_id in self.referees:
            id = re.search(r"\d+", cmd.lower()).group()
            if self.player(int(id)):
                self.msg("^6Referee ^7" + str(caller) + " muted " + self.player(int(id)).name + ".")
                self.player(int(id)).mute()
            else:
                caller.tell("No player with ID: ^2" + id + "^7.")

        elif re.search(r"ref unmute \d+", cmd.lower()) and caller.steam_id in self.referees:
            id = re.search(r"\d+", cmd.lower()).group()
            if self.player(int(id)):
                self.msg("^6Referee ^7" + str(caller) + " unmuted " + self.player(int(id)).name + ".")
                self.player(int(id)).unmute()
            else:
                caller.tell("No player with ID: ^2" + id + "^7.")

        elif re.search(r"ref kick \d+", cmd.lower()) and caller.steam_id in self.referees:
            if self.get_cvar("qlx_allowRefKick", bool):
                id = re.search(r"\d+", cmd.lower()).group()
                if self.player(int(id)):
                    self.msg("^6Referee ^7" + str(caller) + " kicked " + self.player(int(id)).name + ".")
                    self.player(int(id)).kick()
                else:
                    caller.tell("No player with ID: ^2" + id + "^7.")
            else:
                caller.tell("Kicking has been disabled for referees.")

        elif re.search(r"ref tempban \d+", cmd.lower()) and caller.steam_id in self.referees:
            if self.get_cvar("qlx_allowRefKickban", bool):
                id = re.search(r"\d+", cmd.lower()).group()
                if self.player(int(id)):
                    self.msg("^6Referee ^7" + str(caller) + " temporarily kickbanned " + self.player(int(id)).name + ".")
                    self.player(int(id)).tempban()
                else:
                    caller.tell("No player with ID: ^2" + id + "^7.")
            else:
                caller.tell("Kickbanning has been disabled for referees.")

    def cmd_ref(self, player, msg, channel):
        if msg[1].lower() == "allready" and player.steam_id in self.referees:
            if self.game.state == "warmup":
                self.msg("^6Referee ^7" + str(player) + " readied the teams.")
                self.allready()
            else:
                player.tell("The game is already in progress.")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "abort" and player.steam_id in self.referees:
            if self.game.state != "warmup":
                self.msg("^6Referee ^7" + str(player) + " aborted the match.")
                self.abort()
            else:
                player.tell("The match hasn't started yet.")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "pause" and player.steam_id in self.referees:
            if self.game.state != "warmup":
                self.msg("^6Referee ^7" + str(player) + " paused the match.")
                self.pause()
            else:
                player.tell("The match hasn't started yet.")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "unpause" and player.steam_id in self.referees:
            if self.game.state != "warmup":
                self.msg("^6Referee ^7" + str(player) + " unpaused the match.")
                self.unpause()
            else:
                player.tell("The match hasn't started yet.")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "lock" and len(msg) < 3 and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " locked the teams.")
            self.lock()
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "lock" and (msg[2].lower() == "r" or msg[2].lower() == "red") and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " locked the ^1red ^7team.")
            self.lock("red")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "lock" and (msg[2].lower() == "b" or msg[2].lower() == "blue") and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " locked the ^4blue ^7teams")
            self.lock("blue")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "unlock" and len(msg) < 3 and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " unlocked the teams.")
            self.unlock()
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "unlock" and (msg[2].lower() == "r" or msg[2].lower() == "red") and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " unlocked the ^1red ^7team.")
            self.unlock("red")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "unlock" and (msg[2].lower() == "b" or msg[2].lower() == "blue") and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " unlocked the ^4blue ^7team.")
            self.unlock("blue")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "freecam" and (msg[2] == "0" or msg[2].lower() == "off") and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " disabled freecam spectator mode.")
            self.set_cvar("g_teamSpecFreeCam", "0")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "freecam" and (msg[2] == "1" or msg[2].lower() == "on") and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " enabled freecam spectator mode.")
            self.set_cvar("g_teamSpecFreeCam", "1")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "alltalk" and (msg[2] == "0" or msg[2].lower() == "off") and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " disabled communication between teams.")
            self.set_cvar("g_allTalk", "0")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "alltalk" and (msg[2] == "1" or msg[2].lower() == "on") and player.steam_id in self.referees:
            self.msg("^6Referee ^7" + str(player) + " enabled communication between teams.")
            self.set_cvar("g_allTalk", "1")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "put" and (0 <= int(msg[2]) < 64) and (msg[3] == "s" or msg[3] == "spec" or msg[3] == "spectator") and player.steam_id in self.referees:
            if self.player(int(msg[2])):
                self.msg("^6Referee ^7" + str(player) + " moved " + self.player(int(msg[2])).name + " to the spectators.")
                self.player(int(msg[2])).put("spectator")
            else:
                player.tell("No player with ID: ^2" + msg[2] + "^7.")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "mute" and (0 <= int(msg[2]) < 64) and player.steam_id in self.referees:
            if self.player(int(msg[2])):
                self.msg("^6Referee ^7" + str(player) + " muted " + self.player(int(msg[2])).name + ".")
                self.player(int(msg[2])).mute()
            else:
                player.tell("No player with ID: ^2" + msg[2] + "^7.")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "unmute" and (0 <= int(msg[2]) < 64) and player.steam_id in self.referees:
            if self.player(int(msg[2])):
                self.msg("^6Referee ^7" + str(player) + " unmuted " + self.player(int(msg[2])).name + ".")
                self.player(int(msg[2])).unmute()
            else:
                player.tell("No player with ID: ^2" + msg[2] + "^7.")
            return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "kick" and (0 <= int(msg[2]) < 64) and player.steam_id in self.referees:
            if self.get_cvar("qlx_allowRefKick", bool):
                if self.player(int(msg[2])):
                    self.msg("^6Referee ^7" + str(player) + " kicked " + self.player(int(msg[2])).name + ".")
                    self.player(int(msg[2])).unmute()
                else:
                    player.tell("No player with ID: ^2" + msg[2] + "^7.")
                return minqlx.RET_STOP_ALL
            else:
                player.tell("Kicking has been disabled for referees.")
                return minqlx.RET_STOP_ALL

        elif msg[1].lower() == "tempban" and (0 <= int(msg[2]) < 64) and player.steam_id in self.referees:
            if self.get_cvar("qlx_allowRefKickban", bool):
                if self.player(int(msg[2])):
                    self.msg("^6Referee ^7" + str(player) + " temporarily kickbanned " + self.player(int(msg[2])).name + ".")
                    self.player(int(msg[2])).unmute()
                else:
                    player.tell("No player with ID: ^2" + msg[2] + "^7.")
                return minqlx.RET_STOP_ALL
            else:
                player.tell("Kickbanning has been disabled for referees.")
                return minqlx.RET_STOP_ALL

        else:
            return minqlx.RET_STOP_ALL

    def cmd_setrefpass(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE

        self.password = str(msg[1])
        self.referees = []
        player.tell("Referee password changed to: ^2" + str(msg[1]) +"^7; referee list reset.")
        return minqlx.RET_STOP_ALL

    def cmd_getrefpass(self, player, msg, channel):
        player.tell("Referee password is: ^2" + self.password +"^7.")
        return minqlx.RET_STOP_ALL

    def cmd_referees(self, player, msg, channel):
        if self.referees:
            player.tell("^6Referees ^7currently on the server:\n")
            for refs in self.referees:
                for p in self.players():
                    if p.steam_id == refs:
                        player.tell(p.name)
        else:
            player.tell("There are no referees currently on the server.")
        return minqlx.RET_STOP_ALL
