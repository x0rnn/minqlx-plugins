#specs.py by x0rnn to list players spectating you and to check who someone is spectating
#!specs: show players spectating you
#!specwho <id>: show who <id> is spectating
#!specall: show who every spectator is spectating

import minqlx
from collections import defaultdict

class specs(minqlx.Plugin):

    def __init__(self):
        self.add_hook("player_disconnect", self.handle_player_disconnect)
        self.add_command("specs", self.cmd_specs)
        self.add_command("specwho", self.cmd_specwho, usage="<id>")
        self.add_command("specall", self.cmd_specall)

        self.specpos = defaultdict(dict)
        self.playerpos = defaultdict(dict)
        self.match = False

    def handle_player_disconnect(self, player, reason):
        try:
            del self.specpos[str(player.steam_id)]
            del self.playerpos[str(player.steam_id)]
        except KeyError:
            return

    def cmd_specs(self, player, msg, channel):
        if player.team == "spectator":
            player.tell("You must join the game first to use this command.")
            return minqlx.RET_STOP_EVENT

        else:
            player.tell(", ".join([p.name for p in self.teams()["spectator"] if p.state.position == player.state.position]))
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
                        name = pl.name
            if self.match:
                player.tell("{} is spectating {}".format(target_player.name, name))
                self.match = False
            else:
                player.tell("{} is not spectating anyone.".format(target_player.name))
        else:
            player.tell("{} is not a spectator.".format(target_player.name))

    def cmd_specall(self, player, msg, channel):
        for p in self.teams()["spectator"]:
            self.specpos[str(p.steam_id)]["x"] = int(p.state.position.x)
            self.specpos[str(p.steam_id)]["y"] = int(p.state.position.y)
            self.specpos[str(p.steam_id)]["z"] = int(p.state.position.z)
            for pl in self.players():
                if pl.team != "spectator":
                    self.playerpos[str(pl.steam_id)]["x"] = int(pl.state.position.x)
                    self.playerpos[str(pl.steam_id)]["y"] = int(pl.state.position.y)
                    self.playerpos[str(pl.steam_id)]["z"] = int(pl.state.position.z)
                    if abs(self.specpos[str(p.steam_id)]["x"] - self.playerpos[str(pl.steam_id)]["x"]) < 20 and abs(self.specpos[str(p.steam_id)]["y"] - self.playerpos[str(pl.steam_id)]["y"]) < 20 and abs(self.specpos[str(p.steam_id)]["z"] - self.playerpos[str(pl.steam_id)]["z"]) < 20:
                        player.tell("{} is spectating {}".format(p.name, pl.name))
