#!/bin/python
import roomai.common

class SevenKingPublicState(roomai.common.AbstractPublicState):
    """
    """
    def __init__(self):
        """

        """
        super(SevenKingPublicState,self).__init__()
        self.stage            = None
        self.num_players      = None
        self.showed_cards     = None
        self.num_showed_cards = None
        self.num_keep_cards   = None
        self.num_hand_cards   = None
        self.is_fold          = None
        self.num_fold         = None
        self.license_action   = None

    def __deepcopy__(self, newinstance = None, memodict={}):
        """

        Args:
            newinstance:
            memodict:

        Returns:

        """
        if  newinstance is None:
            newinstance = SevenKingPublicState()
        newinstance            = super(SevenKingPublicState,self).__deepcopy__(newinstance = newinstance)

        if self.showed_cards is None:
            newinstance.showed_cards = None
        else:
            newinstance.showed_cards = [card.__deepcopy__() for card in self.showed_cards]
        return newinstance

class SevenKingPrivateState(roomai.common.AbstractPrivateState):
    """
    """
    def __init__(self):
        """

        """
        super(SevenKingPrivateState,self).__init__()
        self.keep_cards   = []

    def __deepcopy__(self, newinstance = None, memodict={}):
        """

        Args:
            newinstance:
            memodict:

        Returns:

        """
        if newinstance is None:
            newinstance = SevenKingPrivateState()
        newinstance            = super(SevenKingPrivateState,self).__deepcopy__(newinstance = newinstance)
        newinstance.keep_cards =  [card.__deepcopy__() for card in self.keep_cards   ]
        return newinstance


class SevenKingPersonState(roomai.common.AbstractPersonState):
    """
    """
    def __init__(self):
        """

        """
        super(SevenKingPersonState,self).__init__()
        self.hand_cards   = []

    def __deepcopy__(self, memodict={}, newinstance = None):
        """

        Args:
            memodict:
            newinstance:

        Returns:

        """
        if newinstance is None:
            newinstance        = SevenKingPersonState()
        newinstance            = super(SevenKingPersonState, self).__deepcopy__(newinstance= newinstance)
        newinstance.hand_cards = [card.__deepcopy__() for card in self.hand_cards]
        return newinstance



