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
        self.getTitle(url)

    @minqlx.thread
    def getTitle(self, url):
        @minqlx.next_frame
        def printTitle(status_code):
            if status_code == 200:
                title = lxml.html.fromstring(www.content)
                try:
                    self.msg("^5URL title: ^7" + title.find(".//title").text)
                except:
                    return
            else:
                self.msg("^5Invalid URL, status code " + str(status_code))

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
            headers = requests.head(url[0]).headers.get('content-type')
            if "text/html" not in headers:
                return
        except:
            return
        try:
            www = requests.get(url[0])
        except requests.exceptions.RequestException:
            return
        www.connection.close() #not sure if this is necessary but just in case
        if www.status_code != requests.codes.ok:
            printTitle(www.status_code)
            return

        printTitle(200)
