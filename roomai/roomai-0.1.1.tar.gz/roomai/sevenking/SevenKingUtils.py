#!/bin/python
import roomai.common

AllSevenKingPatterns = dict()
###
###numCards
AllSevenKingPatterns["p_0"] = ("p_0", 0) ## check
AllSevenKingPatterns["p_1"] = ("p_1", 1)
AllSevenKingPatterns["p_2"] = ("p_2", 2)
AllSevenKingPatterns["p_3"] = ("p_3", 3)
AllSevenKingPatterns["p_4"] = ("p_4", 4)


point_str_to_rank  = {'7':14, 'R':13, 'r':12, '5':11,  '2':10,  '3':9,  'A':8,  'K':7,\
                      'Q':6,  'J':5,   'T':4,   '9':3,   '8':2,   '6':1,   '4':0}
point_rank_to_str  = {14:'7', 13:'R', 12:'r',  11:'5', 10:'2',  9:'3',  8:'A',   7:'K',\
                       6:'Q',  5:'J',   4:'T',   3:'9',   2:'8',   1:'6',  0:'4'}
suit_str_to_rank   = {'Spade':3, 'Heart':2, 'Diamond':1, 'Club':0,  'ForKing':4}
suit_rank_to_str   = {3:'Spade', 2: 'Heart', 1: 'Diamond', 0:'Club', 4:'ForKing'}

class SevenKingPokerCard(roomai.common.PokerCard):
    """
    """
    @property
    def point_rank(self):
        """

        Returns:

        """
        return point_str_to_rank[self.point_str]
    @property
    def suit_rank(self):
        """

        Returns:

        """
        return suit_str_to_rank[self.suit_str]
    def lookup(cls, key):
        """

        Args:
            key:

        Returns:

        """
        return AllSevenKingPokerCards[key]
    def __deepcopy__(self,  memodict={}, newinstance = None):
        """

        Args:
            memodict:
            newinstance:

        Returns:

        """
        if newinstance is None:
            newinstance = AllSevenKingPokerCards[self.key]
        else:
            newinstance = super(SevenKingPokerCard, self).__deepcopy__(newinstance = newinstance)
        return newinstance

AllSevenKingPokerCards = dict()
for point in point_str_to_rank:
    if point != "r" and point != "R":
        for suit in suit_str_to_rank:
            if suit != "ForKing":
                AllSevenKingPokerCards["%s_%s" % (point, suit)] = SevenKingPokerCard("%s_%s" % (point, suit))
AllSevenKingPokerCards["R_ForKing"] = SevenKingPokerCard("R_ForKing")
AllSevenKingPokerCards["r_ForKing"] = SevenKingPokerCard("r_ForKing")
