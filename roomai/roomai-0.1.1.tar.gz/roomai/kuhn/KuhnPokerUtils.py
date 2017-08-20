#!/bin/python
import roomai.common
import copy


class KuhnPokerAction(roomai.common.AbstractAction):
    """
    """
    bet   = 0;
    check = 1;
    def __init__(self, key):
        """

        Args:
            key:
        """
        self.__key = ""
        if key == "bet": self.__key = KuhnPokerAction.bet
        elif key == "check":self.__key = KuhnPokerAction.check
        else:
            raise KeyError("%s is invalid key for Kuhn DouDiZhuPokerAction"%(key))

    @property
    def key(self):
        """

        Returns:

        """
        if self.__key == KuhnPokerAction.bet:
            return "bet"
        else:
            return "check"

    @classmethod
    def lookup(cls, key):
        """

        Args:
            key:

        Returns:

        """
        return AllKuhnActions[key]

    def __deepcopy__(self, memodict={}):
        """

        Args:
            memodict:

        Returns:

        """
        copy = KuhnPokerAction(self.key)
        return copy

AllKuhnActions = {"bet":KuhnPokerAction("bet"),"check":KuhnPokerAction("check")}

class KuhnPokerPublicState(roomai.common.AbstractPublicState):
    """
    """
    def __init__(self):
        """

        """
        self.turn                       = 0
        self.first                      = 0
        self.epoch                      = 0
        self.action_list                = []


    def __deepcopy__(self, memodict={}):
        """

        Args:
            memodict:

        Returns:

        """
        copy = KuhnPokerPublicState()
        copy.turn  = self.turn
        copy.first = self.first
        copy.epoch = self.epoch
        for a in self.action_list:
            copy.action_list.append(a)
        return copy

class KuhnPokerPrivateState(roomai.common.AbstractPrivateState):
    """
    """
    def __init__(self):
        """

        """
        self.hand_cards = []

    def __deepcopy__(self, memodict={}):
        """

        Args:
            memodict:

        Returns:

        """
        copy            = KuhnPokerPrivateState()
        copy.hand_cards = [card for card in self.hand_cards]
        return copy

class KuhnPokerPersonState(roomai.common.AbstractPersonState):
    """
    """
    def __init__(self):
        """

        """
        self.available_actions  = dict()
        self.id                 = 1
        self.card               = 0

    def __deepcopy__(self, memodict={}, newinstance = None):
        """

        Args:
            memodict:
            newinstance:

        Returns:

        """
        copy                   = KuhnPokerPersonState()
        copy.id                = self.id
        copy.card              = self.card
        copy.available_actions = dict()

        if self.available_actions is None:
            copy.available_actions = None
        else:
            for action_key in self.available_actions:
                copy.available_actions[action_key] = self.available_actions[action_key].__deepcopy__()
        return copy
