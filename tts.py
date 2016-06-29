# tts.py by x0rnn, primitive TTS (text-to-speech) system based on arpabet (https://en.wikipedia.org/wiki/Arpabet)
# Use with: https://steamcommunity.com/sharedfiles/filedetails/?id=710007616
# Add 710007616 to qlx_workshopReferences and workshop.txt

import minqlx
import threading
import requests
import json
import time

class tts(minqlx.Plugin):
    def __init__(self):

        self.add_command("tts", self.cmd_tts, 1, usage="<text>")

    def cmd_tts(self, player, msg, channel):
        if len(msg) < 1:
            return minqlx.RET_USAGE

        text = " ".join(msg[1:])
        self.getPhonemes(text)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def getPhonemes(self, text):
        def tts(list):
            for phoneme in list:
                if phoneme not in ",.?!":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.15)

        try:
            url = "http://api.corrasable.com/phonemes"
            params = { "text": text }
            res = requests.post(url, params=params)
        except requests.exceptions.RequestException:
            return

        res = res.json()
        res = res[0]
        try:
            res.remove('N/A')
        except:
            pass
        string = " ".join([str(x) for x in res])
        string = "".join(i for i in string if not i.isdigit())
        list = string.split()

        tts(list)
