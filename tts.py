# tts.py by x0rnn, primitive TTS (text-to-speech) system based on arpabet (https://en.wikipedia.org/wiki/Arpabet)
# Put https://github.com/x0rnn/minqlx-plugins/blob/master/tts.txt in the same directory as this plugin
# Use with: https://steamcommunity.com/sharedfiles/filedetails/?id=710007616
# Add 710007616 to qlx_workshopReferences and workshop.txt

import minqlx
import threading
import time
import re
import csv
import os

class tts(minqlx.Plugin):
    def __init__(self):
        self.add_command("tts", self.cmd_tts, 1, usage="<text>")
        words_list = []
        phonemes_list = []

        with open(os.path.join(os.path.dirname(__file__), "tts.txt") , "r", encoding="utf8") as ph:
            tsv_reader = csv.DictReader(ph, delimiter="\t")
            for w in tsv_reader:
                words_list.append(w["Word"])
                phonemes_list.append(w["Phonemes"])

    def cmd_tts(self, player, msg, channel):
        if len(msg) < 1:
            return minqlx.RET_USAGE

        text = " ".join(msg[1:])
        text = text.lower()
        self.getPhonemes(text, player)
        return minqlx.RET_STOP_ALL

    @minqlx.thread
    def getPhonemes(self, text, player):
        valid_words = []
        invalid_words = []
        phonemes = []

        def tts(ph_list):
            for phoneme in list:
                self.play_sound("sound/tts/" + phoneme + ".wav")
                time.sleep(0.15)

        text = re.sub(r'[.,"\-?:!;0-9]', '', text)
        text_list = text.split()
        for w in text_list:
            if w in words_list:
                valid_words.append(w)
            else:
                invalid_words.append(w)

        if len(invalid_words) != 0:
            player.tell("Didn't find the following words: '{}', can't do TTS.".format(' '.join(invalid_words)))
        else:
            for w in valid_words:
                phonemes.append(phonemes_list[words_list.index(w)])
            ph_string = ' '.join(phonemes)
            ph_list = ph_string.split()
            tts(ph_list)
