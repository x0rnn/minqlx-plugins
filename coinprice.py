#coinprice.py by x0rnn, shows current bitcoin/ethereum/litecoin price and info

import minqlx
import requests

class coinprice(minqlx.Plugin):
    def __init__(self):

        self.add_command(("bitcoin", "btc"), self.cmd_bitcoin, 0)
        self.add_command(("ethereum", "eth"), self.cmd_ethereum, 0)
        self.add_command(("litecoin", "ltc"), self.cmd_litecoin, 0)
        self.c1 = "^1"
        self.c2 = "^1"

    def cmd_bitcoin(self, player, msg, channel):
        self.getCoin("bitcoin")

    def cmd_ethereum(self, player, msg, channel):
        self.getCoin("ethereum")

    def cmd_litecoin(self, player, msg, channel):
        self.getCoin("litecoin")

    @minqlx.thread
    def getCoin(self, coin):
        @minqlx.next_frame
        def printCoin():
            if coin == "bitcoin":
                self.msg("^7Bitcoin price: ^3${}^7, 1h change: {}{}pct (${})^7, 24h change: {}{}pct (${})".format(round(price_usd, 2), self.c1, change_1h, round((price_usd / 100) * change_1h, 2), self.c2, change_24h, round((price_usd / 100) * change_24h, 2)))
            elif coin == "ethereum":
                self.msg("^7Ethereum price: ^3${}^7, 1h change: {}{}pct (${})^7, 24h change: {}{}pct (${})".format(round(price_usd, 2), self.c1, change_1h, round((price_usd / 100) * change_1h, 2), self.c2, change_24h, round((price_usd / 100) * change_24h, 2)))
            elif coin == "litecoin":
                self.msg("^7Litecoin price: ^3${}^7, 1h change: {}{}pct (${})^7, 24h change: {}{}pct (${})".format(round(price_usd, 2), self.c1, change_1h, round((price_usd / 100) * change_1h, 2), self.c2, change_24h, round((price_usd / 100) * change_24h, 2)))

        try:
            r = requests.get("https://api.coinmarketcap.com/v1/ticker/" + coin)
            try:
                r = r.json()
            except:
                return
        except requests.exceptions.RequestException:
            return
        price_usd = r[0]["price_usd"]
        change_1h = r[0]["percent_change_1h"]
        change_24h = r[0]["percent_change_24h"]

        if change_1h < 0:
            self.c1 = "^1"
        else:
            self.c1 = "^2"
        if change_24h < 0:
            self.c2 = "^1"
        else:
            self.c2 = "^2"

        printCoin()
