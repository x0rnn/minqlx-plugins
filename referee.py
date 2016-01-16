# referee.py, gives referee status to a player with the password and enables him the following console commands:
#########################################################################
# help          - Lists all referee commands
# allready      - Force all players to be 'ready' and start the match.
# abort         - Abandon the current game and return to warmup.
# pause         - Pause the current match indefinitely.
# unpause       - Unause the current match.
# lock [r/b]    - Stop players from joining the team.
# unlock [r/b]  - Allow players to join the team.
# speclock      - Disable freecam spectator mode for dead players.
# specunlock    - Enable freecam spectator mode for dead players.
# alltalk <0/1> - Disable/enable communication between teams.
#########################################################################
# The commands need to be prefixed with /ref, for example: /ref allready
# To get referee status, type /ref pass "password" (without quotation marks)
# The initial password is set on line 26 of this file ("change_me"), change it to something unique.
# Change the password in-game/between matches with !refpass "password" (without quotation marks)

import minqlx

class referee(minqlx.Plugin):
    def __init__(self):
        self.add_hook("client_command", self.handle_client_command)
        self.add_command("refpass", self.cmd_refpass, 5, usage="<password> (no spaces)")

        self.password = "change_me"
        self.referees = []

    def handle_client_command(self, caller, cmd):
        if cmd.lower() == "ref pass " + self.password:
            self.referees.append(caller.steam_id)
            caller.tell("^5Password correct, referee status granted. /ref help to list all commands.")

        elif cmd.lower() == "ref help" and caller.steam_id in self.referees:
            caller.tell("^3Use /ref <cmd> [arg]:\n"
                        "^5allready           ^3- ^7Force all players to be 'ready' and start the match.\n"
                        "^5abort              ^3- ^7Abandon the current game and return to warmup.\n"
                        "^5pause              ^3- ^7Pause the current match indefinitely.\n"
                        "^5unpause            ^3- ^7Unause the current match.\n"
                        "^5lock [r/b]         ^3- ^7Stop players from joining the team.\n"
                        "^5unlock [r/b]       ^3- ^7Allow players to join the team.\n"
                        "^5speclock           ^3- ^7Disable freecam spectator mode for dead players.\n"
                        "^5specunlock         ^3- ^7Enable freecam spectator mode for dead players.\n"
                        "^5alltalk [0/1]      ^3- ^7Disable/enable communication between teams.")

        elif cmd.lower() == "ref allready" and caller.steam_id in self.referees:
            if self.game.state == "warmup":
                self.msg("Referee " + str(caller) + " readied the teams.")
                self.allready()
            else:
                caller.tell("The game is already in progress.")

        elif cmd.lower() == "ref abort" and caller.steam_id in self.referees:
            if self.game.state != "warmup":
                self.msg("Referee " + str(caller) + " aborted the match.")
                self.abort()
            else:
                caller.tell("The match hasn't started yet.")

        elif cmd.lower() == "ref pause" and caller.steam_id in self.referees:
            if self.game.state != "warmup":
                self.msg("Referee " + str(caller) + " paused the match.")
                self.pause()
            else:
                caller.tell("The match hasn't started yet.")

        elif cmd.lower() == "ref unpause" and caller.steam_id in self.referees:
            if self.game.state != "warmup":
                self.msg("Referee " + str(caller) + " unpaused the match.")
                self.unpause()
            else:
                caller.tell("The match hasn't started yet.")

        elif cmd.lower() == "ref lock" and caller.steam_id in self.referees:
            self.msg("Referee " + str(caller) + " locked the teams.")
            self.lock()

        elif cmd.lower() == "ref lock r" and caller.steam_id in self.referees:
            self.msg("Referee " + str(caller) + " locked the ^1red ^7team.")
            self.lock("red")

        elif cmd.lower() == "ref lock b" and caller.steam_id in self.referees:
            self.msg("Referee " + str(caller) + " locked the ^4blue ^7team.")
            self.lock("blue")

        elif cmd.lower() == "ref unlock" and caller.steam_id in self.referees:
            self.msg("Referee " + str(caller) + " unlocked the teams.")
            self.unlock()

        elif cmd.lower() == "ref unlock r" and caller.steam_id in self.referees:
            self.msg("Referee " + str(caller) + " unlocked the ^1red ^7team.")
            self.unlock("red")

        elif cmd.lower() == "ref unlock b" and caller.steam_id in self.referees:
            self.msg("Referee " + str(caller) + " unlocked the ^4blue ^7team.")
            self.unlock("blue")

        elif cmd.lower() == "ref speclock" and caller.steam_id in self.referees:
            self.msg("Referee " + str(caller) + " disabled freecam spectator mode.")
            self.set_cvar("g_teamSpecFreeCam", "0")

        elif cmd.lower() == "ref specunlock" and caller.steam_id in self.referees:
            self.msg("Referee " + str(caller) + " enabled freecam spectator mode.")
            self.set_cvar("g_teamSpecFreeCam", "1")

        elif cmd.lower() == "ref alltalk 0" and caller.steam_id in self.referees:
            self.msg("Referee " + str(caller) + " disabled communication between teams.")
            self.set_cvar("g_allTalk", "0")

        elif cmd.lower() == "ref alltalk 1" and caller.steam_id in self.referees:
            self.msg("Referee " + str(caller) + " enabled communication between teams.")
            self.set_cvar("g_allTalk", "1")

    def cmd_refpass(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE

        self.password = msg[1]
        self.referees = []
        player.tell("Referee password changed; referee list reset.")
        return minqlx.RET_STOP_ALL
