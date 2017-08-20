#!/bin/python
#coding:utf-8

import roomai.common
import copy

class StageSpace:
    """
    """
    firstStage  = 1
    secondStage = 2
    thirdStage  = 3
    fourthStage = 4


class TexasHoldemAction(roomai.common.AbstractAction):
    """
    """
    # 弃牌
    Fold        = "Fold"
    # 过牌
    Check       = "Check"
    # 更注
    Call        = "Call"
    # 加注
    Raise       = "Raise"
    # all in
    AllIn       = "Allin"
    def __init__(self, key):
        """

        Args:
            key:
        """
        opt_price = key.strip().split("_")
        self.__option = opt_price[0]
        self.__price  = int(opt_price[1])
        self.__key    = "%s_%d"%(self.option, self.price)

    @property
    def key(self):
        """

        Returns:

        """
        return self.__key
    @property
    def option(self):
        """

        Returns:

        """
        return self.__option
    @property
    def price(self):
        """

        Returns:

        """
        return self.__price

    @classmethod
    def lookup(cls, key):
        """

        Args:
            key:

        Returns:

        """
        if key not in AllTexasActions:
            AllTexasActions[key] = TexasHoldemAction(key)
        return AllTexasActions[key]

    def __deepcopy__(self, memodict={}, newinstance = None):
        """

        Args:
            memodict:
            newinstance:

        Returns:

        """
        if self.key not in AllTexasActions:
            AllTexasActions[self.key] = TexasHoldemAction(self.key)
        return AllTexasActions[self.key]

AllTexasActions = dict()


class TexasHoldemPublicState(roomai.common.AbstractPublicState):
    """
    """
    def __init__(self):
        """

        """
        self.stage              = None
        self.num_players        = None
        self.dealer_id          = None
        self.public_cards       = None
        self.num_players        = None
        self.big_blind_bet      = None

        #state of players
        self.is_fold                        = None
        self.num_quit                       = None
        self.is_allin                       = None
        self.num_allin                      = None
        self.is_needed_to_action            = None
        self.num_needed_to_action           = None

        # who is expected to take a action
        self.turn               = None

        #chips is array which contains the chips of all players
        self.chips              = None

        #bets is array which contains the bets from all players
        self.bets               = None

        #max_bet = max(self.bets)
        self.max_bet_sofar      = None
        #the raise acount
        self.raise_account      = None

        self.previous_id        = None
        self.previous_action    = None

    def __deepcopy__(self, memodict={}):
            """

            Args:
                memodict:

            Returns:

            """
            copyinstance = TexasHoldemPublicState()

            copyinstance.stage         = self.stage
            copyinstance.num_players   = self.num_players
            copyinstance.dealer_id     = self.dealer_id
            copyinstance.big_blind_bet = self.big_blind_bet

            if self.public_cards is None:
                copyinstance.public_cards = None
            else:
                copyinstance.public_cards = [self.public_cards[i].__deepcopy__() for i in xrange(len(self.public_cards))]


            ######## quit, allin , needed_to_action
            copy.num_quit = self.num_quit
            if self.is_fold is None:
                copyinstance.is_fold = None
            else:
                copyinstance.is_fold = [self.is_fold[i] for i in xrange(len(self.is_fold))]

            copyinstance.num_allin = self.num_allin
            if self.is_allin is None:
                copyinstance.is_allin = None
            else:
                copyinstance.is_allin = [self.is_allin[i] for i in xrange(len(self.is_allin))]

            copyinstance.num_needed_to_action = self.num_needed_to_action
            if self.is_needed_to_action is None:
                copyinstance.is_needed_to_action = None
            else:
                copyinstance.is_needed_to_action = [self.is_needed_to_action[i] for i in
                                                    xrange(len(self.is_needed_to_action))]

            # chips is array which contains the chips of all players
            if self.chips is None:
                copyinstance.chips = None
            else:
                copyinstance.chips = [self.chips[i] for i in xrange(len(self.chips))]

            # bets is array which contains the bets from all players
            if self.bets is None:
                copyinstance.bets = None
            else:
                copyinstance.bets = [self.bets[i] for i in xrange(len(self.bets))]

            copyinstance.max_bet_sofar = self.max_bet_sofar
            copyinstance.raise_account = self.raise_account
            copyinstance.turn = self.turn

            copyinstance.previous_id = self.previous_id
            if self.previous_action is None:
                copyinstance.previous_action = None
            else:
                copyinstance.previous_action = self.previous_action.__deepcopy__()

            ### isterminal, scores
            copyinstance.is_terminal = self.is_terminal
            if self.scores is None:
                copyinstance.scores = None
            else:
                copyinstance.scores = [self.scores[i] for i in xrange(len(self.scores))]

            return copyinstance


class TexasHoldemPrivateState(roomai.common.AbstractPrivateState):
    """
    """
    keep_cards = []
    hand_cards = []

    def __deepcopy__(self, memodict={}):
        """

        Args:
            memodict:
        """
        copy = TexasHoldemPrivateState()
        if self.keep_cards is None:
            copy.keep_cards = None
        else:
            copy.keep_cards = [self.keep_cards[i].__deepcopy__() for i in xrange(len(self.keep_cards))]

        if self.hand_cards is None:
            copy.hand_cards = None
        else:
            copy.hand_cards = [[] for i in xrange(len(self.hand_cards))]
            for i in xrange(len(self.hand_cards)):
                copy.hand_cards[i] = [self.hand_cards[i][j].__deepcopy__() for j in xrange(len(self.hand_cards[i]))]


class TexasHoldemPersonState(roomai.common.AbstractPersonState):
    """
    """
    id                =    0
    hand_cards        =    []
    available_actions =    dict()

    def __deepcopy__(self, memodict={}):
        """

        Args:
            memodict:

        Returns:

        """
        copyinstance    = TexasHoldemPersonState()
        copyinstance.id = self.id
        if self.hand_cards is not None:
            copyinstance.hand_cards = [self.hand_cards[i].__deepcopy__() for i in xrange(len(self.hand_cards))]
        else:
            copyinstance.hand_cards = None

        if self.available_actions is not None:
            copyinstance.available_actions = dict()
            for key in self.available_actions:
                copyinstance.available_actions[key] = self.available_actions[key].__deepcopy__()
        else:
            copyinstance.available_actions = None
        return copyinstance


AllCardsPattern = dict()
#0     1           2       3           4                                    5     6
#name, isStraight, isPair, isSameSuit, [SizeOfPair1, SizeOfPair2,..](desc), rank, cards
AllCardsPattern["Straight_SameSuit"] = \
["Straight_SameSuit",   True,  False, True,  [],        100, []]
AllCardsPattern["4_1"] = \
["4_1",                 False, True,  False, [4,1],     98,  []]
AllCardsPattern["3_2"] = \
["3_2",                 False, True,  False, [3,2],     97,  []]
AllCardsPattern["SameSuit"] = \
["SameSuit",            False, False, True,  [],        96,  []]
AllCardsPattern["Straight_DiffSuit"] = \
["Straight_DiffSuit",   True,  False, False, [],        95,  []]
AllCardsPattern["3_1_1"] = \
["3_1_1",               False, True,  False, [3,1,1],   94,  []]
AllCardsPattern["2_2_1"] = \
["2_2_1",               False, True,  False, [2,2,1],   93,  []]
AllCardsPattern["2_1_1_1"] = \
["2_1_1_1",             False, True,  False, [2,1,1,1], 92,  []]
AllCardsPattern["1_1_1_1_1"] = \
["1_1_1_1_1",           False, True,  False, [1,1,1,1,1],91, []]




