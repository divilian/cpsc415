#!/usr/bin/env python3
'''
CPSC 415 -- Homework #5 support file
Stephen Davies, University of Mary Washington, fall 2023
'''

import random
import sys
import re
import importlib
from collections import namedtuple
import logging
from abc import ABC, abstractmethod

Card = namedtuple('Card', ['name','category'])

# These really ought to be sets, but to avoid inter-player shenanigans, I'll
# make them inviolable tuples.
suspects = tuple( Card(s,'SUSPECT') for s in ['mustard','plum','green',
    'scarlet', 'white','peacock'] )
weapons = tuple( Card(w,'WEAPON') for w in ['knife','revolver','rope',
    'candlestick', 'wrench','leadpipe'] )
rooms = tuple( Card(r,'ROOM') for r in ['diningroom','ballroom',
    'billiardroom', 'study','conservatory','kitchen', 'hall','lounge',
    'library'] )


class Deck():
    def __init__(self):
        self.suspects = list(suspects)
        self.weapons = list(weapons)
        self.rooms = list(rooms)
        self.gen_solution()
        self.shuffle()

    def gen_solution(self):
        self.murderer = random.choice(self.suspects)
        self.suspects.remove(self.murderer)
        self.murder_weapon = random.choice(self.weapons)
        self.weapons.remove(self.murder_weapon)
        self.crime_scene = random.choice(self.rooms)
        self.rooms.remove(self.crime_scene)

    def shuffle(self):
        self.cards = self.suspects + self.weapons + self.rooms
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop(0)


class Clue():
    def __init__(self, player_classes):
        if len(player_classes) != 3:
            raise "Number of players must be 3!"
        self.player_classes = player_classes
        
    def play(self):
        self.deck = Deck()
        self._init_players()
        self.pns = [0,1,2]   # "player numbers"
        random.shuffle(self.pns)   # Random who goes first, etc
        self.players = [ self.players[n] for n in self.pns ]
        self.hands = [ self.hands[n] for n in self.pns ]
        while True:
            player = self.players.pop(0)
            hand = self.hands.pop(0)
            if player.dqd:
                logging.info(f"(Skipping {player}, who DQ'd.)")
            elif player.ready_to_accuse():
                accusation = player.get_accusation()
                logging.info(f"{player} accuses: "
                    f"{tuple( s.name for s in accusation )}.")
                # TODO: inform other players of accusation.
                if accusation == (self.deck.murderer,
                    self.deck.murder_weapon, self.deck.crime_scene):
                    logging.info(f"{player} wins!")
                    #return self._player_name_of(player)
                    return player
                else:
                    logging.info(f"{player} DQ'd.")
                    player.dqd = True
                    if all([ p.dqd for p in self.players ]):
                        logging.warning("All players DQ'd!")
                        return "Tie"
            else:
                logging.info(f"{player} suggesting...")
                suggestion = player.get_suggestion()
                logging.info(f"{player} suggested: "
                    f"{tuple( s.name for s in suggestion )}.")
                for resp_num in range(0,len(self.players)):
                    responding_pl = self.players[resp_num]
                    card = responding_pl.handle_suggestion(
                        player.player_num, suggestion)
                    if card:
                        logging.info(f"{responding_pl} shows: {card.name}.")
                    else:
                        if any([ s in self.hands[resp_num]
                                for s in suggestion ]):
                            sys.exit(str(responding_pl) + " lied! (Said " +
                                f"they couldn't help <" +
                                ",".join([ s.name for s in suggestion ]) +
                                "> but actually had <" + 
                                ",".join([ c.name
                                    for c in self.hands[resp_num] ])+ ">")
                        logging.info(f"{responding_pl} can't help.")
                    for p in [player] + self.players:
                        p.publicly_observe(player.player_num,
                            suggestion, responding_pl.player_num,
                            card != None)
                    if card:
                        player.secretly_observe(
                            responding_pl.player_num, card)
                        break
                
            self.players.append(player)
            self.hands.append(hand)

    def _init_players(self):
        self.hands = [ set(), set(), set() ]
        num = 0
        try:
            while True:
                self.hands[num] |= {self.deck.deal()}
                num = (num + 1) % len(self.player_classes)
        except:
            pass
        self.players = [ p(h,n)
            for p, h, n in zip(self.player_classes, self.hands, range(1,4)) ]
        for p in self.players:
            logging.info(f"{p}: {[ c.name for c in p.hand ]}.")

    def _player_name_of(self, player):
        return re.sub('_CluePlayer','',type(player).__name__)


# Abstract superclass for player classes to inherit from.
class CluePlayer(ABC):
    def __init__(self, player_num, player_name):
        self.player_num = player_num
        self.player_name = player_name
        self.dqd = False

    @abstractmethod
    def ready_to_accuse(self):
        """
        Return True if you know (or think you know) the answer, and are ready
        to risk all by declaring it.
        """
        pass

    @abstractmethod
    def get_accusation(self):
        """
        Return a tuple of exactly three Cards: a SUSPECT, a WEAPON, and a ROOM,
        in that order. You will either win the game, or be DQ'd.
        """
        pass

    @abstractmethod
    def get_suggestion(self):
        """
        Return a tuple of exactly three Cards: a SUSPECT, a WEAPON, and a ROOM,
        in that order. This is what you want to "suggest" as the mystery answer
        to the next player in line. You will be told which card they show you,
        if any, in a future call to your .secretly_observe() method. If they do
        not have any of your named cards, your .secretly_observe() method will
        never be called; only your .publicly_observe() method.
        """
        pass

    @abstractmethod
    def publicly_observe(self, suggesting_player_num, suggestion,
        responding_player_num, revealed_a_card):
        """
        This method will be called on your player whenever anyone takes a turn.
        It tells you that a certain player made a suggestion (a tuple with
        three named cards, in suspect/weapon/room order) to another player,
        and whether or not that player secretly showed them a card.
        """
        pass

    @abstractmethod
    def secretly_observe(self, responding_player_num, card):
        """
        This method will be called on your player whenever you take your turn
        and make a suggestion. The card passed will be the card that the
        responding player secretly showed you (one of the three you named).
        """
        pass

    @abstractmethod
    def handle_suggestion(self, suggesting_player_num, suggestion):
        """
        This method will be called on your player whenever the player before
        you suggests a murder solution (three named cards, in suspect/weapon/
        room order). You must return one of the three cards, or None if you
        don't have any of them.
        """
        pass

    def __str__(self):
        return self.__repr__()
    def __repr__(self):
        return f"Player {self.player_num} ({self.player_name})"


def print_usage():
    print("Usage: clue.py player1userid player2userid player3userid.")

def get_player_class(userid):
    try:
        stud_module = importlib.import_module(userid + '_CluePlayer')
        Student_class = getattr(stud_module,userid + '_CluePlayer')
        this_module = importlib.import_module('clue')
        superclass = getattr(this_module,'CluePlayer')
    except Exception as err:
        print(str(err))
        sys.exit(2)
    if not issubclass(Student_class, superclass):
        print(f"{Student_class.__name__} doesn't inherit from CluePlayer.")
        sys.exit(3)
    return Student_class


if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) != 4:
        print_usage()
        sys.exit()
    player_classes = [ get_player_class(u) for u in sys.argv[1:4] ]
    game = Clue(player_classes)
    print(f"Winner: {game.play()}.")
