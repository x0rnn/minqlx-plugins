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
                if phoneme == aa:
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.150)
                if phoneme == "ae":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.100)
                if phoneme == "ah":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.041)
                if phoneme == "ao":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.150)
                if phoneme == "aw":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.190)
                if phoneme == "ay":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.150)
                if phoneme == "eh":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.070)
                if phoneme == "er":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.100)
                if phoneme == "ey":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.150)
                if phoneme == "ih":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.070)
                if phoneme == "iy":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.100)
                if phoneme == "ow":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.150)
                if phoneme == "oy":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.150)
                if phoneme == "uh":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.070)
                if phoneme == "uw":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.080)
                if phoneme == "b":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.070)
                if phoneme == "ch":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.100)
                if phoneme == "d":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.070)
                if phoneme == "dh":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.070)
                if phoneme == "f":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.080)
                if phoneme == "g":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.080)
                if phoneme == "hh":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.070)
                if phoneme == "jh":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.080)
                if phoneme == "k":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.080)
                if phoneme == "l":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.080)
                if phoneme == "m":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.080)
                if phoneme == "n":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.070)
                if phoneme == "ng":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.080)
                if phoneme == "p":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.070)
                if phoneme == "r":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.080)
                if phoneme == "s":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.100)
                if phoneme == "sh":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.100)
                if phoneme == "t":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.070)
                if phoneme == "th":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.080)
                if phoneme == "v":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.070)
                if phoneme == "w":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.080)
                if phoneme == "z":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.080)
                if phoneme == "y":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.080)
                if phoneme == "zh":
                    self.play_sound("sound/tts/" + phoneme + ".wav")
                    time.sleep(0.080)

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
