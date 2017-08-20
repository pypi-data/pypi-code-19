#!/bin/python
import roomai.common
import copy


class FiveCardStudPrivateState(roomai.common.AbstractPrivateState):
    """
    """
    all_hand_cards    = None

    def __deepcopy__(self, memodict={}):
        """

        Args:
            memodict:

        Returns:

        """
        copyinstance = FiveCardStudPrivateState()
        if self.all_hand_cards is None:
            copyinstance.all_hand_cards = None
        else:
            copyinstance.all_hand_cards = [self.all_hand_cards[i].__deepcopy__() for i in xrange(len(self.all_hand_cards))]
        return copyinstance


class FiveCardStudPublicState(roomai.common.AbstractPublicState):
    """
    """
    first_hand_cards      = None
    second_hand_cards     = None
    third_hand_cards      = None
    fourth_hand_cards     = None
    fifth_hand_cards      = None

    is_quit               = None
    num_quit              = None
    is_raise              = None
    num_raise             = None
    is_needed_to_action   = None
    num_needed_to_action  = None

    # chips is array which contains the chips of all players
    chips = None

    # bets is array which contains the bets from all players
    bets = None

    upper_bet              = None
    floor_bet              = None
    max_bet_sofar          = None

    turn                   = None
    round                  = None
    num_players            = None

    previous_id            = None
    previous_action        = None
    previous_round         = None

    is_terminal            = None
    scores                 = None

    def __deepcopy__(self,memodict={}):
        """

        Args:
            memodict:

        Returns:

        """
        copyinstance = FiveCardStudPublicState()

        if self.first_hand_cards is None:
            copyinstance.first_hand_cards = None
        else:
            copyinstance.first_hand_cards = [self.first_hand_cards[i].__deepcopy__() for i in xrange(len(self.first_hand_cards))]

        if self.second_hand_cards is None:
            copyinstance.second_hand_cards = None
        else:
            copyinstance.second_hand_cards = [self.second_hand_cards[i].__deepcopy__() for i in xrange(len(self.second_hand_cards))]

        if self.third_hand_cards is None:
            copyinstance.third_hand_cards = None
        else:
            copyinstance.third_hand_cards = [self.third_hand_cards[i].__deepcopy__() for i in xrange(len(self.third_hand_cards))]

        if self.fourth_hand_cards is None:
            copyinstance.fourth_hand_cards = None
        else:
            copyinstance.fourth_hand_cards = [self.fourth_hand_cards[i].__deepcopy__() for i in xrange(len(self.fourth_hand_cards))]

        if self.fifth_hand_cards is None:
            copyinstance.fifth_hand_cards = None
        else:
            copyinstance.fifth_hand_cards = [self.fifth_hand_cards[i].__deepcopy__() for i in xrange(len(self.fifth_hand_cards))]

        copy.num_quit          = self.num_quit
        if self.is_quit is None:
            copyinstance.is_quit = None
        else:
            copyinstance.is_quit = [self.is_quit[i] for i in xrange(len(self.is_quit))]

        copyinstance.num_raise = self.num_raise
        if self.is_raise is None:
            copyinstance.is_raise = None
        else:
            copyinstance.is_raise  = [self.is_raise[i] for i in xrange(len(self.is_raise))]

        copyinstance.num_needed_to_action = self.num_needed_to_action
        if self.is_needed_to_action is None:
            copyinstance.is_needed_to_action = None
        else:
            copyinstance.is_needed_to_action = [self.is_needed_to_action[i] for i in xrange(len(self.is_needed_to_action))]

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

        copyinstance.upper_bet     = self.upper_bet
        copyinstance.floor_bet     = self.floor_bet
        copyinstance.max_bet_sofar = self.max_bet_sofar

        copyinstance.turn          = self.turn
        copyinstance.round         = self.round
        copyinstance.num_players   = self.num_players

        copyinstance.previous_id     = self.previous_id
        if self.previous_action is None:
            copyinstance.previous_action = None
        else:
            copyinstance.previous_action = self.previous_action.__deepcopy__()
        copyinstance.previous_round  = self.previous_round

        copyinstance.is_terminal = self.is_terminal

        if self.scores is None:
            copyinstance.scores = None
        else:
            copyinstance.scores = [self.scores[i] for i in xrange(len(self.scores))]

        return copyinstance


class FiveCardStudPersonState(roomai.common.AbstractPersonState):
    """
    """
    id                = None
    available_actions = None

    first_hand_card   = None
    second_hand_card  = None
    third_hand_card   = None
    fourth_hand_card  = None
    fifth_hand_card   = None


    def __deepcopy__(self, memodict={}, newinstance = None):
        """

        Args:
            memodict:
            newinstance:

        Returns:

        """
        copyinstance    = FiveCardStudPersonState()
        copyinstance.id = self.id

        if self.available_actions is not None:
            copyinstance.available_actions = dict()
            for key in self.available_actions:
                copyinstance.available_actions[key] = self.available_actions[key].__deepcopy__()
        else:
            copyinstance.available_actions = None

        if self.first_hand_card is not None:
            copyinstance.first_hand_card = self.first_hand_card.__deepcopy__()
        else:
            copyinstance.first_hand_card = None

        if self.second_hand_card is not None:
            copyinstance.second_hand_card = self.second_hand_card.__deepcopy__()
        else:
            copyinstance.second_hand_card = None

        if self.third_hand_card is not None:
            copyinstance.third_hand_card = self.third_hand_card.__deepcopy__()
        else:
            copyinstance.third_hand_card = None

        if self.fourth_hand_card is not None:
            copyinstance.fourth_hand_card = self.fourth_hand_card.__deepcopy__()
        else:
            copyinstance.fourth_hand_card = None

        if self.fifth_hand_card is not None:
            copyinstance.fifth_hand_card = self.fifth_hand_card.__deepcopy__()
        else:
            copyinstance.fifth_hand_card = None


        return copyinstance

