#!/bin/python
import roomai.common

                                                    #0     1           2       3           4                                    5
                                                    #name, isStraight, isSameSuit, isNumRelated, [SizeOfPair1, SizeOfPair2,..](desc), rank
FiveCardStudAllCardsPattern = dict()
FiveCardStudAllCardsPattern["Straight_SameSuit"] = ["Straight_SameSuit", True, True, False, [], 100]
FiveCardStudAllCardsPattern["4_1"]               = ["4_1", False, False, True, [4, 1], 98]
FiveCardStudAllCardsPattern["3_2"]               = ["3_2", False, False, True, [3, 2], 97]
FiveCardStudAllCardsPattern["SameSuit"]          = ["SameSuit", False, True, False, [], 96]
FiveCardStudAllCardsPattern["Straight_DiffSuit"] = ["Straight_DiffSuit", True, False, False, [], 95]
FiveCardStudAllCardsPattern["3_1_1"]             = ["3_1_1", False, False, True, [3, 1, 1], 94]
FiveCardStudAllCardsPattern["2_2_1"]             = ["2_2_1", False, False, True, [2, 2, 1], 93]
FiveCardStudAllCardsPattern["2_1_1_1"]           = ["2_1_1_1", False, False, True, [2, 1, 1, 1], 92]
FiveCardStudAllCardsPattern["1_1_1_1_1"]         = ["1_1_1_1_1", False, False, True, [1, 1, 1, 1, 1], 91]


class FiveCardStudPokerCard(roomai.common.PokerCard):
    """
    """

    def get_suit_rank(self):
        """

        Returns:

        """
        suit_str_to_rank = {'Spade': 3, 'Heart': 2, 'Club': 1, 'Diamond':0}
        return suit_str_to_rank[self.suit_str]

    @classmethod
    def compare(cls, pokercard1, pokercard2):
        """

        Args:
            pokercard1:
            pokercard2:

        Returns:

        """
        pr1 = pokercard1.get_point_rank()
        pr2 = pokercard2.get_point_rank()
        if pr1 != pr2:
            return pr1-pr2
        else:
            return pokercard1.get_suit_rank() - pokercard2.get_suit_rank()


    def __deepcopy__(self, memodict={}, newinstance = None):
        """

        Args:
            memodict:
            newinstance:

        Returns:

        """
        if newinstance is None:
            newinstance = FiveCardStudAllPokerCards[self.key]
        return newinstance

    @classmethod
    def lookup(cls, key):
        """

        Args:
            key:

        Returns:

        """
        return FiveCardStudAllPokerCards[key]


FiveCardStudAllPokerCards = dict()
for point_str in roomai.common.common.point_str_to_rank:
    if point_str != 'r' and point_str != "R":
        for suit_str in roomai.common.common.suit_str_to_rank:
            if suit_str != "ForKing":
                FiveCardStudAllPokerCards["%s_%s"%(point_str,suit_str)] = FiveCardStudPokerCard("%s_%s"%(point_str,suit_str))
FiveCardStudAllPokerCards["r_ForKing"] = (FiveCardStudPokerCard("r_ForKing"))
FiveCardStudAllPokerCards["R_ForKing"] = (FiveCardStudPokerCard("R_ForKing"))
