#stats.py by x0rnn, show some simple kill stats: kills, deaths, k/d ratio, kills per minute
#x0rnn: K:50/D:9[R:5.56] KPM:7.14

import minqlx

class stats(minqlx.Plugin):
    def __init__(self):
        self.add_command("stats", self.cmd_stats, 0)

    def cmd_stats(self, player, msg, channel):
        if int(player.stats.deaths) != 0:
            msg = "{}^7: K:{}/D:{}[R:{}] KPM:{}".format(player.name, player.stats.kills, player.stats.deaths, round((int(player.stats.kills) / int(player.stats.deaths)), 2), round((int(player.stats.kills) / int(player.stats.time / 60000)), 2))
            self.msg(msg)
        else:
            msg = "{}^7: K:{}/D:0[R:{}] KPM:{}".format(player.name, player.stats.kills, player.stats.kills, round((int(player.stats.kills) / int(player.stats.time / 60000)), 2))
            self.msg(msg)
