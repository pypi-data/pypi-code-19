#!/bin/python
import os
import roomai.common
from roomai.doudizhu.DouDiZhuPokerAction import DouDiZhuActionElement
import copy


class DouDiZhuHandCards:
    """
    """
    def __init__(self, cardstr):
        """

        Args:
            cardstr:
        """
        self.cards = [0 for i in range(DouDiZhuActionElement.total_normal_cards)]
        for c in cardstr:
            idx = DouDiZhuActionElement.str_to_rank[c]
            self.cards[idx] += 1
            if idx >= DouDiZhuActionElement.total_normal_cards:
                raise Exception("%s is invalid for a handcard" % (cardstr))

        self.num_cards = sum(self.cards)
        self.count2num = [0 for i in range(DouDiZhuActionElement.total_normal_cards)]
        for count in self.cards:
            self.count2num[count] += 1

        strs = []
        for h in range(len(self.cards)):
            for count in range(self.cards[h]):
                strs.append(DouDiZhuActionElement.rank_to_str[h])
        strs.sort()
        self.__key = "".join(strs)

    def compute_key(self):
        """

        Returns:

        """
        strs = []
        for h in range(len(self.cards)):
            for count in range(self.cards[h]):
                strs.append(DouDiZhuActionElement.rank_to_str[h])
        strs.sort()
        return "".join(strs)

    @property
    def key(self):
        """

        Returns:

        """
        return self.__key


    def add_cards(self, cards):
        """

        Args:
            cards:
        """
        if isinstance(cards, str) == True:
            cards = DouDiZhuHandCards(cards)

        for c in range(len(cards.cards)):
            count = cards.cards[c]
            self.num_cards += count
            self.count2num[self.cards[c]] -= 1
            self.cards[c] += count
            self.count2num[self.cards[c]] += 1

        self.__key = self.compute_key()


    def remove_cards(self, cards):
        """

        Args:
            cards:
        """
        if isinstance(cards, str) == True:
            cards = DouDiZhuHandCards(cards)

        for c in range(len(cards.cards)):
            count = cards.cards[c]
            self.num_cards -= count
            self.count2num[self.cards[c]] -= 1
            self.cards[c] -= count
            self.count2num[self.cards[c]] += 1

        self.__key = self.compute_key()

    def remove_action(self, action):
        """

        Args:
            action:
        """
        str = action.key
        if str == 'x' or str == 'b':
            str = ''
        self.remove_cards(DouDiZhuHandCards(str))
        self.__key = self.compute_key()

    def __deepcopy__(self, memodict={}, newinstance = None):
        """

        Args:
            memodict:
            newinstance:

        Returns:

        """
        return DouDiZhuHandCards(self.key)

class DouDiZhuPrivateState(roomai.common.AbstractPrivateState):
    """
    """
    def __init__(self):
        """

        """
        self.keep_cards = []

    def __deepcopy__(self, memodict={}, newinstance = None):
        """

        Args:
            memodict:
            newinstance:

        Returns:

        """
        if newinstance is None:
            newinstance = DouDiZhuPrivateState()
        newinstance.keep_cards = self.keep_cards.__deepcopy__()
        return newinstance


class DouDiZhuPublicState(roomai.common.AbstractPublicState):
    """
    """
    def __init__(self):
        """

        """
        self.landlord_candidate_id = -1
        self.landlord_id = -1
        self.license_playerid = -1
        self.license_action = None
        self.continuous_cheat_num = 0
        self.is_response = False

        self.keep_cards = None
        self.first_player = -1
        self.turn = -1
        self.phase = -1
        self.epoch = -1

        self.previous_id = -1
        self.previous_action = None

    def __deepcopy__(self, memodict={}, newinstance = None):
        """

        Args:
            memodict:
            newinstance:

        Returns:

        """
        if newinstance is None:
            newinstance = DouDiZhuPublicState()
        newinstance = super(DouDiZhuPublicState, self).__deepcopy__(newinstance=newinstance)

        newinstance.landlord_candidate_id = self.landlord_candidate_id
        newinstance.landlord_id = self.landlord_id
        newinstance.license_playerid = self.license_playerid
        if self.license_action is None:
            newinstance.license_action  = None
        else:
            newinstance.license_action = self.license_action.__deepcopy__()
        newinstance.continuous_cheat_num = self.continuous_cheat_num
        newinstance.is_response = self.is_response

        if self.keep_cards == None:
            newinstance.keep_cards = None
        else:
            newinstance.keep_cards = self.keep_cards.__deepcopy__()

        newinstance.first_player = self.first_player
        newinstance.turn  = self.turn
        newinstance.phase = self.phase
        newinstance.epoch = self.epoch

        newinstance.previous_id = self.previous_id
        if self.previous_action is None:
            newinstance.previous_action = None
        else:
            newinstance.previous_action = self.previous_action.__deepcopy__()

        return newinstance

class DouDiZhuPersonState(roomai.common.AbstractPersonState):
    """
    """
    def __init__(self):
        """

        """
        self.id                = None
        self.hand_cards        = None
        self.available_actions = dict()
    def __deepcopy__(self, memodict={}, newinstance = None):
        """

        Args:
            memodict:
            newinstance:

        Returns:

        """
        if newinstance is None:
            newinstance = DouDiZhuPersonState()
        newinstance.id = self.id

        if self.hand_cards is None:
            newinstance.hand_cards = None
        else:
            newinstance.hand_cards = self.hand_cards.__deepcopy__()

        if self.available_actions is None:
            newinstance.available_actions = None
        else:
            newinstance.available_actions = dict()
            for str in self.available_actions:
                newinstance.available_actions[str] = self.available_actions[str]
        return newinstance

