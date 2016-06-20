#urltitle.py by x0rnn, prints the title of a website/youtube link, etc. posted in chat
#sudo apt-get install python3-lxml
#sudo python3.5 -m pip install lxml
#sudo python3.5 -m pip install tld


import minqlx
import threading
import requests
import re
import lxml.html
import socket
from tld import get_tld

class urltitle(minqlx.Plugin):
    def __init__(self):

        self.add_hook("chat", self.handle_chat)

    def handle_chat(self, player, msg, channel):
        if channel != "chat":
            return
        if msg[0] == "!":
            return
        url = re.findall(r'http[s]?://[^\s<>"]+|www\.[^\s<>"]+', msg)[:1]
        if not url:
            return
        try:
            self.getTitle(url)
        except:
            return

    @minqlx.thread
    def getTitle(self, url):
        if not url[0].lower().startswith("http"):
            url[0] = ''.join(('http://', url[0]))
        try:
            tld = get_tld(url[0])
            try:
                socket.gethostbyname(tld)
            except:
                return
        except:
            return
        try:
            www = requests.get(url[0])
        except requests.exceptions.RequestException:
            return
        if www.status_code != requests.codes.ok:
            return

        @minqlx.next_frame
        def printTitle():
            title = lxml.html.fromstring(www.content)
            self.msg("^5URL title: ^7" + title.find(".//title").text)

        printTitle()