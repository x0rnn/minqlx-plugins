#specs.py by x0rnn to list players spectating you and to check who someone is spectating
import minqlx

class specs(minqlx.Plugin):

    def __init__(self):
        self.add_command("specs", self.cmd_specs)
        self.add_command("specwho", self.cmd_specwho, usage="<id>")

        self.match = False

    def cmd_specs(self, player, msg, channel):
        if player.team == "spectator":
            player.tell("You must join the game first to use this command.")
            return minqlx.RET_STOP_EVENT

        else:
            for pl in self.players():
                if pl.team == "spectator":
                    if pl.state.position == player.state.position:
                        player.tell(pl.name)
            return minqlx.RET_STOP_EVENT

    def cmd_specwho(self, player, msg, channel):
        if len(msg) < 2:
            return minqlx.RET_USAGE

        try:
            ident = int(msg[1])
            target_player = None
            if 0 <= ident < 64:
                target_player = self.player(ident)
                ident = target_player.steam_id
        except ValueError:
            channel.reply("No player with that ID.")
            return
        except minqlx.NonexistentPlayerError:
            channel.reply("Invalid client ID.")
            return

        if target_player.team == "spectator":
            for pl in self.players():
                if pl.team != "spectator":
                    specx = int(target_player.state.position.x)
                    specy = int(target_player.state.position.y)
                    specz = int(target_player.state.position.z)
                    playerx = int(pl.state.position.x)
                    playery = int(pl.state.position.y)
                    playerz = int(pl.state.position.z)
                    if abs(specx - playerx) < 20 and abs(specy - playery) < 20 and abs(specz - playerz) < 20:
                        self.match = True
            if self.match:
                player.tell("{} is spectating {}".format(target_player.name, pl.name))
                self.match = False
            else:
                player.tell("{} is not spectating anyone.".format(target_player.name))
        else:
            player.tell("{} is not a spectator.".format(target_player.name))
