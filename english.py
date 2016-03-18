# english.py - English motherfucker, do you speak it?
# Use with: https://steamcommunity.com/sharedfiles/filedetails/?id=647835676
import minqlx

class english(minqlx.Plugin):
    def __init__(self):
        self.add_command("english", self.cmd_english, 2)

    def cmd_english(self, player, msg, channel):
        self.play_sound("sound/misc/english.wav")

    def play_sound(self, path):
        for p in self.players():
            super().play_sound(path, p)
