#fastrespawn.py by x0rnn
#if you selfkill, you respawn in 1.8 seconds like in Q3 instead of waiting 3 seconds (QL default)

import minqlx
 
class fastrespawn(minqlx.Plugin):
    def __init__(self):
        self.add_hook("death", self.handle_death)
 
    def handle_death(self, victim, killer, data):
        @minqlx.delay(1.8)
        def delay_spawn():
            minqlx.player_spawn(victim.id)
 
        if data['MOD'] == "SUICIDE":
            delay_spawn()
