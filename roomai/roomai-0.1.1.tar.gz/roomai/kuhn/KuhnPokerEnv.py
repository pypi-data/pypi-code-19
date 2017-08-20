#!/bin/python
import random
import math
import copy
import roomai.common
import roomai.kuhn.KuhnPokerUtils

class KuhnPokerEnv(roomai.common.AbstractEnv):
    """
    """

    #@override
    def init(self, params=dict()):
        """

        Args:
            params:

        Returns:

        """

        if "record_history" in params:
            self.record_history = params["record_history"]
        else:
            self.record_history = False

        if "start_turn" in params:
            self.start_turn = params["start_turn"]
        else:
            self.start_turn = int(random.random() * 2)

        self.available_action = dict()
        self.available_action[roomai.kuhn.KuhnPokerUtils.KuhnPokerAction("check").key] = roomai.kuhn.KuhnPokerAction.lookup("check")
        self.available_action[roomai.kuhn.KuhnPokerUtils.KuhnPokerAction("bet").key]   = roomai.kuhn.KuhnPokerAction.lookup("bet")

        self.private_state = roomai.kuhn.KuhnPokerUtils.KuhnPokerPrivateState()
        self.public_state  = roomai.kuhn.KuhnPokerUtils.KuhnPokerPublicState()
        self.person_states = [roomai.kuhn.KuhnPokerUtils.KuhnPokerPersonState() for i in xrange(2)]

        self.public_state_history  = []
        self.private_state_history = []
        self.person_states_history = []

        card0 = math.floor(random.random() * 3)
        card1 = math.floor(random.random() * 3)
        while card0 == card1:
            card0 = math.floor(random.random() * 3)
        self.private_state.hand_cards = [card0, card1]

        self.public_state.turn          = self.start_turn
        self.public_state.first         = self.public_state.turn
        self.public_state.epoch         = 0
        self.public_state.action_list   = []
        self.public_state.is_terminal   = False
        self.public_state.scores        = None
        self.person_states[0].id = 0
        self.person_states[0].card      = card0
        self.person_states[1].id        = 1
        self.person_states[1].card      = card1

        self.person_states[self.public_state.turn].available_actions = self.available_action

        self.__gen_history__()
        infos = self.__gen_infos__()

        
        return  infos, self.public_state, self.person_states, self.private_state

    #@override
    def forward(self, action):
        """

        Args:
            action:

        Returns:

        """
        self.person_states[self.public_state.turn].available_actions = dict()
        self.public_state.epoch                                     += 1
        self.public_state.turn                                       = (self.public_state.turn+1)%2
        self.public_state.action_list.append(action.key)

        if self.public_state.epoch == 1:
            self.public_state.is_terminal = False
            self.public_state.scores      = []
            self.person_states[self.public_state.turn].available_actions = self.available_action

            self.__gen_history__()
            infos = self.__gen_infos__()
            return infos, self.public_state, self.person_states, self.private_state

        elif self.public_state.epoch == 2:
            scores = self.evaluteTwo()
            if scores is not None:
                self.public_state.is_terminal = True
                self.public_state.scores      = scores

                self.__gen_history__()
                infos = self.__gen_infos__()
                return infos,self.public_state, self.person_states, self.private_state
            else:
                self.public_state.is_terminal = False
                self.public_state.scores      = []
                self.person_states[self.public_state.turn].available_actions = self.available_action

                self.__gen_history__()
                infos                         = self.__gen_infos__()
                return infos,self.public_state, self.person_states, self.private_state

        elif self.public_state.epoch == 3:
            self.public_state.is_terminal = True
            self.public_state.scores      = self.evaluteThree()

            self.__gen_history__()
            infos                         = self.__gen_infos__()
            return infos,self.public_state, self.person_states, self.private_state

        else:
            raise Exception("KuhnPoker has 3 turns at most")


    #@Overide
    @classmethod
    def compete(cls, env, players):
        """

        Args:
            env:
            players:

        Returns:

        """

        infos, public_state, person_state, private_state = env.init()
        for i in xrange(len(players)):
            players[i].receive_info(infos[i])

        while public_state.is_terminal == False:
            turn = infos[-1].public_state.turn
            action = players[turn].take_action()
            infos,public_state, person_state, private_state = env.forward(action)
            for i in xrange(len(players)):
                players[i].receive_info(infos[i])

        return public_state.scores



    def WhoHasHigherCard(self):
        """

        Returns:

        """
        hand_cards = self.private_state.hand_cards
        if hand_cards[0] > hand_cards[1]:
            return 0
        else:
            return 1

    def evaluteTwo(self):
        """

        Returns:

        """
        win    = self.WhoHasHigherCard()
        first  = self.public_state.first
        scores = [0, 0];
        actions = self.public_state.action_list

        if actions[0] == "check" and \
           actions[1] == "bet":
            return None
        
        if actions[0] == actions[1] and \
           actions[0] == "check":
            scores[win]   = 1;
            scores[1-win] = -1
            return scores;

        if actions[0] == "bet" and \
           actions[1] == "check":
            scores[first]   = 1;
            scores[1-first] = -1
            return scores;

        if actions[0] == actions[1] and \
           actions[0] == "bet":
            scores[win]   = 2
            scores[1-win] = -2
            return scores;


    def evaluteThree(self):
        """

        Returns:

        """
        first   = self.public_state.first 
        win     = self.WhoHasHigherCard()
        scores  = [0, 0]

        if self.public_state.action_list[2] == "check":
            scores[1 - first] = 1;
            scores[first]     = -1
        else:
            scores[win]   = 2;
            scores[1-win] = -2
        return scores;
       
