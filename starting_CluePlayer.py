'''
CPSC 415 -- Homework #5 support file
Stephen Davies, University of Mary Washington, fall 2023
'''

from clue import CluePlayer, suspects, weapons, rooms, Card

# Throughout this file, you can refer to the global variables "suspects",
# "weapons", and "rooms", which are tuples of "Card" objects telling you what
# cards are in the game, period. You can even try this right now:
#
# >>> print(suspects)
# >>> print(weapons)
# >>> print(rooms)
#
# Each Card object has a name and a category, accessible with the dot (".")
# notation:
# >>> print(f"{suspects[0].name} is a {suspects[0].category}")
# mustard is a SUSPECT


class starting_CluePlayer(CluePlayer):

    def __init__(self, hand, player_num):
        """
        Change 'starting' to your player name, and add anything else you want
        to this constructor. I've created an inst var "hand" since I think
        you'll want that. It's a list of the Cards you're dealt at the start
        of the game.
        """
        super().__init__(player_num, 'starting')
        self.hand = hand

    def ready_to_accuse(self):
        """
        Return True if you know (or think you know) the answer, and are ready
        to risk all by declaring it.
        """
        pass

    def get_accusation(self):
        """
        Return a tuple of exactly three Cards: a SUSPECT, a WEAPON, and a ROOM,
        in that order. You will either win the game, or be DQ'd.
        """
        pass

    def get_suggestion(self):
        """
        Return a tuple of exactly three Cards: a SUSPECT, a WEAPON, and a ROOM,
        in that order. This is what you want to "suggest" as the mystery answer
        to the next player in line. You will be told which card they show you,
        if any, in a future call to your .secretly_observe() method. If they do
        not have any of your named cards, your .secretly_observe() method will
        never be called; only your .publicly_observe() method will be.
        """
        pass

    def publicly_observe(self, suggesting_player_num, suggestion,
        responding_player_num, revealed_a_card):
        """
        This method will be called on your player whenever anyone makes a
        suggestion (including you). It tells you that a certain player made a
        suggestion (a tuple with three named cards, in suspect/weapon/room
        order) to another player, and whether or not that second player
        secretly showed them a card.
        """
        pass

    def secretly_observe(self, responding_player_num, card):
        """
        This method will be called on your player whenever you take your turn
        and make a suggestion, and one of your opponents does have one of the
        cards you named. The card passed will be the card that the responding
        player secretly showed you (one of the three you named). This method is
        *not* called if an opponent does not have any of your three cards; the
        way you'll know that is by paying attention to your .publicly_observe()
        method.
        """
        pass

    def handle_suggestion(self, suggesting_player_num, suggestion):
        """
        This method will be called on your player whenever the player before
        you suggests a murder solution (three named cards, in suspect/weapon/
        room order). You must return one of the three cards to secretly show
        them, or None if you don't have any of them.
        """
        pass

