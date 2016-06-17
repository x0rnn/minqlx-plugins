# english.py - English motherfucker, do you speak it?
# also added "Denied!" from Q3 and STFU (https://www.youtube.com/watch?v=Y0CfLJd-2LQ)
# Use with: https://steamcommunity.com/sharedfiles/filedetails/?id=647835676
# Add 647835676 to qlx_workshopReferences and workshop.txt
import minqlx

class english(minqlx.Plugin):
    def __init__(self):
        self.add_command("english", self.cmd_english, 1)
        self.add_command("denied", self.cmd_denied, 1)
        self.add_command("stfu", self.cmd_stfu, 1)

    def cmd_english(self, player, msg, channel):
        self.play_sound("sound/misc/english.wav")

    def cmd_denied(self, player, msg, channel):
        self.play_sound("sound/misc/denied.wav")

    def cmd_stfu(self, player, msg, channel):
        self.play_sound("sound/misc/stfu.wav")
