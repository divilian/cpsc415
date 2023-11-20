'''
CPSC 415 -- Homework #5 support file
Stephen Davies, University of Mary Washington, fall 2023
'''

from clue import CluePlayer, suspects, weapons, rooms, Card

import random

class random_CluePlayer(CluePlayer):
    def __init__(self, hand, player_num):
        super().__init__(player_num, 'random')
        self.hand = hand
        self.num_rounds = 0
    def ready_to_accuse(self):
        # I'll wait a while, then accuse.
        if self.num_rounds > random.randint(200,300) < self.num_rounds:
            return True
        else:
            return False
    def get_accusation(self):
        return ( random.choice(tuple(suspects)), random.choice(tuple(weapons)),
            random.choice(tuple(rooms)) )
    def get_suggestion(self):
        self.num_rounds += 1
        return ( random.choice(tuple(suspects)), random.choice(tuple(weapons)),
            random.choice(tuple(rooms)) )
    def publicly_observe(self, suggesting_player_num, suggestion,
        responding_player_num, revealed_a_card):
        # I'm a random player, and I simply don't care!
        pass
    def secretly_observe(self, responding_player_num, card):
        # I'm a random player, and I simply don't care!
        pass
    def handle_suggestion(self, suggesting_player_num, suggestion):
        suggestion = list(suggestion)
        random.shuffle(suggestion)
        for card in suggestion:
            if card in self.hand:
                return card
        return None
