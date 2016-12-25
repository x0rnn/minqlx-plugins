# titlerank.py by x0rnn, gives a player a title rank of: Admin, VIP, Regular, Member, Dork
# When the player joins the server, everyone is notified with the following message:
# for Admin: "All rise for Admin <name>!"
# for Dork: "Attention, Dork <name> has joined!"
# others: "Welcome <rank> <name>!"
# No other minqlx permissions are given

import minqlx

PLAYER_KEY = "minqlx:players:{}:titlerank"

class titlerank(minqlx.Plugin):
    def __init__(self):
        self.add_hook("player_loaded", self.handle_player_loaded, priority=minqlx.PRI_LOWEST)
        self.add_command("setrank", self.cmd_setrank, 4, usage="<id> <rank>")
        self.add_command("delrank", self.cmd_delrank, 4, usage="<id>")

        self.ranks = ['Admin', 'VIP', 'Regular', 'Member', 'Dork']

    def cmd_setrank(self, player, msg, channel):
        if len(msg) < 3:
             return minqlx.RET_USAGE

        try:
            ident = int(msg[1])
            target_player = None
            if 0 <= ident < 64:
                target_player = self.player(ident)
                ident = target_player.steam_id
        except ValueError:
            channel.reply("Invalid ID. Use either a client ID or a SteamID64.")
            return
        except minqlx.NonexistentPlayerError:
            channel.reply("Invalid client ID. Use either a client ID or a SteamID64.")
            return

        rank = msg.split()[-1]
        if rank.lower() in (rank.lower() for rank in self.ranks):
            rank_key = PLAYER_KEY.format(self.player(int(msg[1])).steam_id)
            if rank_key in self.db:
                getrank = self.db[rank_key]
                player.tell(self.player(int(msg[1])).clean_name + " already has a title rank of " + getrank + ". Please delete first with !delrank <id> to change.")
                return minqlx.RET_STOP_ALL
            else:
                if rank.lower() == "admin":
                    self.db[rank_key] = "Admin"
                    player.tell("{} has been given the title rank of Admin.".format(self.player(int(msg[1])).clean_name))
                    return minqlx.RET_STOP_ALL
                if rank.lower() == "vip":
                    self.db[rank_key] = "VIP"
                    player.tell("{} has been given the title rank of VIP.".format(self.player(int(msg[1])).clean_name))
                    return minqlx.RET_STOP_ALL
                if rank.lower() == "regular":
                    self.db[rank_key] = "Regular"
                    player.tell("{} has been given the title rank of Regular.".format(self.player(int(msg[1])).clean_name))
                    return minqlx.RET_STOP_ALL
                if rank.lower() == "member":
                    self.db[rank_key] = "Member"
                    player.tell("{} has been given the title rank of Member.".format(self.player(int(msg[1])).clean_name))
                    return minqlx.RET_STOP_ALL
                if rank.lower() == "dork":
                    self.db[rank_key] = "Dork"
                    player.tell("{} has been given the title rank of Dork.".format(self.player(int(msg[1])).clean_name))
                    return minqlx.RET_STOP_ALL
        else:
            player.tell("Available ranks are: Admin, VIP, Regular, Member, Dork")
            return minqlx.RET_STOP_ALL

    def cmd_delrank(self, player, msg, channel):
        if len(msg) < 2:
             return minqlx.RET_USAGE

        try:
            ident = int(msg[1])
            target_player = None
            if 0 <= ident < 64:
                target_player = self.player(ident)
                ident = target_player.steam_id
        except ValueError:
            channel.reply("Invalid ID. Use either a client ID or a SteamID64.")
            return
        except minqlx.NonexistentPlayerError:
            channel.reply("Invalid client ID. Use either a client ID or a SteamID64.")
            return

            rank_key = PLAYER_KEY.format(ident)
            del self.db[rank_key]
            player.tell("{} has been cleared of his title rank.".format(target_player.clean_name))
            return minqlx.RET_STOP_ALL
    
    def handle_player_loaded(self, player):
        rank_key = PLAYER_KEY.format(player.steam_id)
        if rank_key in self.db:
            greet = self.db[rank_key]
            if greet.lower() == "admin":
                self.msg("All rise for ^5{}^7 {}^7!".format(greet, player.name))
            elif greet.lower() == "dork":
                self.msg("Attention, ^1{}^7 {}^7 has joined!".format(greet, player.name))
            else:
                self.msg("Welcome ^5{}^7 {}^7!".format(greet, player.name))
