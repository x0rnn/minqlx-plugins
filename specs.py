#list players spectating you
import minqlx

class specs(minqlx.Plugin):

    def __init__(self):
        self.add_command("specs", self.cmd_specs)

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
