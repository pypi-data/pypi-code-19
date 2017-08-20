#!/bin/python
#coding:utf-8
import random
import roomai.common
import sys

class TexasHoldemRandomPlayer(roomai.common.AbstractPlayer):
    """
    """
    def __init__(self):
        """

        """
        self.available_actions = None
        self.info              = None
           
    def receive_info(self, info):
        """

        Args:
            info:
        """
        self.info              = info
        self.available_actions = info.person_state.available_actions

    def take_action(self):

        '''
        print "\n\n\n"
        if self.info.public_state.previous_id is not None:
            print "previous_id", self.info.public_state.previous_id
        if self.info.public_state.previous_action is not None:
            print "previous_action", self.info.public_state.previous_action.key()
        print "stage", self.info.public_state.stage
        print "is_fold", self.info.public_state.is_fold, self.info.public_state.num_quit
        print "is_allin", self.info.public_state.is_allin, self.info.public_state.num_allin
        print "is_needed_action",self.info.public_state.is_needed_to_action, self.info.public_state.num_needed_to_action
        print "turn:",self.info.public_state.turn
        print "chips:",self.info.public_state.chips
        print "bets:",self.info.public_state.bets
        print "max_bet_sofar:",self.info.public_state.max_bet_sofar
        print "big_dealer:",self.info.public_state.dealer_id
        '''

        idx  = int(random.random() * len(self.available_actions))
        keys = self.available_actions.keys()
        '''
        print idx, len(keys)
        print keys
        print keys[idx]
        print self.available_actions[keys[idx]]
        sys.stdout.flush()
        '''

        return self.available_actions[keys[idx]]

    def reset(self):
        """

        """
        pass
