#!/bin/python
#coding:utf-8

import random
import copy
import itertools

from roomai.doudizhu.DouDiZhuPokerInfo   import *
from roomai.doudizhu.DouDiZhuPokerAction import *

class DouDiZhuPokerEnv(roomai.common.AbstractEnv):
    """
    """

    def __init__(self):
        """

        """
        self.public_state  = DouDiZhuPublicState()
        self.private_state = DouDiZhuPrivateState()
        self.person_states = [DouDiZhuPersonState() for i in range(3)]



    def update_license(self, turn, action):
        """

        Args:
            turn:
            action:
        """
        if action.pattern[0] != "i_cheat":
            self.public_state.license_playerid = turn
            self.public_state.license_action   = action 
            

    def update_cards(self, turn, action):
        """

        Args:
            turn:
            action:
        """
        self.person_states[turn].hand_cards.remove_action(action)


    def update_phase_bid2play(self):
        """

        """
        self.public_state.phase                 = 1
        
        self.public_state.landlord_id           = self.public_state.landlord_candidate_id
        self.public_state.license_playerid      = self.public_state.turn
        self.public_state.continuous_cheat_num  = 0
        self.public_state.is_response           = False

        landlord_id = self.public_state.landlord_id
        self.public_state.keep_cards = DouDiZhuHandCards(self.private_state.keep_cards.key)
        self.person_states[landlord_id].hand_cards.add_cards(self.private_state.keep_cards)


    #@Overide
    def init(self, params = dict()):
        """

        Args:
            params:

        Returns:

        """

        if "allcards" in params:
            self.allcards = [c for c in params["allcards"]]
        else:
            self.cards = []
            for i in range(13):
                for j in range(4):
                    self.cards.append(DouDiZhuActionElement.rank_to_str[i])
            self.cards.append(DouDiZhuActionElement.rank_to_str[13])
            self.cards.append(DouDiZhuActionElement.rank_to_str[14])
            random.shuffle(self.cards)

        if "record_history" in params:
            self.record_history = params["record_history"]
        else:
            self.record_history = False

        if "start_turn" in params:
            self.start_turn = params["start_turn"]
        else:
            self.start_turn = int(random.random() * 2)

        for i in range(3):
            tmp = self.cards[i*17:(i+1)*17]
            tmp.sort()
            self.person_states[i].hand_cards = DouDiZhuHandCards("".join(tmp))

        keep_cards = DouDiZhuHandCards([self.cards[-1], self.cards[-2], self.cards[-3]])
        self.private_state.keep_cards =  keep_cards;
        
        self.public_state.firstPlayer         = self.start_turn
        self.public_state.turn                = self.public_state.firstPlayer
        self.public_state.phase               = 0
        self.public_state.epoch               = 0
        
        self.public_state.landlord_id         = -1
        self.public_state.license_playerid    = self.public_state.turn
        self.public_state.license_action      = None
        self.public_state.is_terminal         = False
        self.public_state.scores              = [0,0,0]

        turn = self.public_state.turn
        self.person_states[turn].available_actions = DouDiZhuPokerEnv.available_actions(self.public_state, self.person_states[turn])

        infos = self.__gen_infos__()
        self.__gen_history__()

        return infos, self.public_state, self.person_states, self.private_state


    ## we need ensure the action is valid
    #@Overide
    def forward(self, action):
        """

        Args:
            action:

        Returns:

        """

        if self.is_action_valid(action, self.public_state, self.person_states[self.public_state.turn]) is False:
            raise  ValueError("%s action is invalid"%(action.key))

        turn = self.public_state.turn
        if self.public_state.phase == 0:
            if action.pattern[0] == "i_bid":
                self.public_state.landlord_candidate_id = turn

            if self.public_state.epoch == 3 and self.public_state.landlord_candidate_id == -1:
                self.public_state.is_terminal = True
                self.public_state.scores      = [0.0, 0.0, 0.0]

                self.__gen_history__()
                infos = self.__gen_infos__()
                return infos, self.public_state, self.person_states, self.private_state

            if (self.public_state.epoch == 2 and self.public_state.landlord_candidate_id != -1)\
                or self.public_state.epoch == 3:
                self.update_phase_bid2play()


                self.public_state.previous_id = turn
                self.public_state.previous_action = action
                self.public_state.epoch += 1
                self.person_states[self.public_state.turn].available_actions = DouDiZhuPokerEnv.available_actions(
                    self.public_state, self.person_states[self.public_state.turn])

                self.__gen_history__()
                infos = self.__gen_infos__()

                return infos, self.public_state, self.person_states, self.private_state


        else: #phase == play

            if action.pattern[0] != "i_cheat":
                
                self.update_cards(turn,action)
                self.update_license(turn,action)
                self.public_state.continuous_cheat_num = 0
    
                num = self.person_states[turn].hand_cards.num_cards
                if num == 0:
                    self.public_state.previous_id = turn
                    self.public_state.previous_action = action
                    self.public_state.epoch += 1
                    if turn == self.public_state.landlord_id:
                        self.public_state.is_terminal                           = True
                        self.public_state.scores                                = [-1,-1,-1]
                        self.public_state.scores[self.public_state.landlord_id] = 2
                    else:
                        self.public_state.is_terminal                           = True
                        self.public_state.scores                                = [1,1,1]
                        self.public_state.scores[self.public_state.landlord_id] = -2
                    self.__gen_history__()
                    infos = self.__gen_infos__()
                    return infos, self.public_state, self.person_states, self.private_state
            else:
                self.public_state.continuous_cheat_num += 1


        self.public_state.turn   = (turn+1)%3


        if self.public_state.continuous_cheat_num == 2:
            self.public_state.is_response          = False
            self.public_state.continuous_cheat_num = 0
        else:
            self.public_state.is_response = True


        self.public_state.previous_id         = turn
        self.public_state.previous_action     = action
        self.public_state.epoch              += 1
        self.person_states[self.public_state.turn].available_actions = DouDiZhuPokerEnv.available_actions(self.public_state, self.person_states[self.public_state.turn])
         
        self.__gen_history__()
        infos = self.__gen_infos__()

        return infos, self.public_state, self.person_states, self.private_state


    #@override
    @classmethod
    def compete(cls, env, players):
        """

        Args:
            env:
            players:

        Returns:

        """
        infos ,public_state, person_states, private_state= env.init()

        for i in range(len(players)):
            players[i].receive_info(infos[i])

        while public_state.is_terminal == False:
            turn = public_state.turn
            action = players[turn].takeAction()
            infos, public_state, person_states, private_state = env.forward(action)
            for i in range(len(players)):
                players[i].receive_info(infos[i])

        return public_state.scores



    @classmethod
    def available_actions(cls, public_state, person_state):
        """

        Args:
            public_state:
            person_state:

        Returns:

        """

        patterns = []
        if public_state.phase == 0:
            patterns.append(AllPatterns["i_cheat"])
            patterns.append(AllPatterns["i_bid"])
        else:
            if public_state.is_response == False:
                for p in AllPatterns:
                    if p != "i_cheat" and p != "i_invalid":
                        patterns.append(AllPatterns[p])
            else:
                patterns.append(public_state.license_action.pattern)
                if public_state.license_action.pattern[6] == 1:
                    patterns.append(AllPatterns["p_4_1_0_0_0"])  # rank = 10
                    patterns.append(AllPatterns["x_rocket"])  # rank = 100
                if public_state.license_action.pattern[6] == 10:
                    patterns.append(AllPatterns["x_rocket"])  # rank = 100
                patterns.append(AllPatterns["i_cheat"])

        is_response = public_state.is_response
        license_act = public_state.license_action
        actions = dict()

        for pattern in patterns:
            numMaster = pattern[1]
            numMasterPoint = pattern[2]
            isStraight = pattern[3]
            numSlave = pattern[4]
            MasterCount = -1
            SlaveCount = -1

            if numMaster > 0:
                MasterCount = int(numMaster / numMasterPoint)

            if "i_invalid" == pattern[0]:
                continue

            if "i_cheat" == pattern[0]:
                action_key = DouDiZhuPokerAction.master_slave_cards_to_key([DouDiZhuActionElement.cheat], [])
                action     = DouDiZhuPokerAction.lookup(action_key)
                if cls.is_action_valid(action,public_state, person_state) == True:
                    actions[action_key] = action
                continue

            if "i_bid" == pattern[0]:
                action_key = DouDiZhuPokerAction.master_slave_cards_to_key([DouDiZhuActionElement.bid], [])
                action     = DouDiZhuPokerAction.lookup(action_key)
                if cls.is_action_valid(action, public_state,person_state) == True:
                    actions[action_key] = action
                continue

            if pattern[0] == "x_rocket":
                if person_state.hand_cards.cards[DouDiZhuActionElement.r] == 1 and \
                                person_state.hand_cards.cards[DouDiZhuActionElement.R] == 1:
                    action_key  = DouDiZhuPokerAction.master_slave_cards_to_key([DouDiZhuActionElement.r, DouDiZhuActionElement.R], [])
                    action      = DouDiZhuPokerAction.lookup(action_key)
                    if cls.is_action_valid(action,public_state,person_state) == True:
                        actions[action_key] = action
                continue

            if pattern[1] + pattern[4] > person_state.hand_cards.num_cards:
                continue
            sum1 = 0

            for count in range(MasterCount, 5, 1):
                sum1 += person_state.hand_cards.count2num[count]
            if sum1 < numMasterPoint:
                continue

            ### action with cards
            mCardss = []
            mCardss = DouDiZhuPokerEnv.extractMasterCards(person_state.hand_cards,  pattern)

            for mCards in mCardss:
                if numSlave == 0:
                    action_key   = DouDiZhuPokerAction.master_slave_cards_to_key(mCards, [])
                    action       = DouDiZhuPokerAction.lookup(action_key)
                    if cls.is_action_valid(action, public_state,person_state) == True:
                        actions[action_key] = action
                    continue

                sCardss = DouDiZhuPokerEnv.extractSlaveCards(person_state.hand_cards, mCards, pattern)
                for sCards in sCardss:
                    action_key  = DouDiZhuPokerAction.master_slave_cards_to_key(mCards, sCards)
                    action      = DouDiZhuPokerAction.lookup(action_key)
                    if cls.is_action_valid(action, public_state,person_state) == True:
                        actions[action_key] = action
        return actions



    @classmethod
    def is_action_valid(cls,action, public_state, person_state):
        '''
        print "is_action_valid_______________________________________________________________"
        print public_state.turn
        print person_state.hand_cards.num_cards
        print person_state.hand_cards.key
        print action.key
        '''

        if action.pattern[0] == "i_invalid":
            return False

        if cls.is_action_from_handcards(person_state.hand_cards, action) == False:
            return False

        turn        = public_state.turn
        license_id  = public_state.license_playerid
        license_act = public_state.license_action
        phase       = public_state.phase

        if phase == 0:
            if action.pattern[0] not in ["i_cheat", "i_bid"]:
                return False
            return True

        if phase == 1:
            if action.pattern[0] == "i_bid":    return False

            if public_state.is_response == False:
                if action.pattern[0] == "i_cheat": return False
                return True

            else:  # response
                if action.pattern[0] == "i_cheat":  return True
                ## not_cheat
                if action.pattern[6] > license_act.pattern[6]:
                    return True
                elif action.pattern[6] < license_act.pattern[6]:
                    return False
                elif action.maxMasterPoint - license_act.maxMasterPoint > 0:
                    return True
                else:
                    return False

    @classmethod
    def is_action_from_handcards(cls, hand_cards, action):
        """

        Args:
            hand_cards:
            action:

        Returns:

        """
        flag = True
        if action.pattern[0] == "i_cheat":  return True
        if action.pattern[0] == "i_bid":    return True
        if action.pattern[0] == "i_invalid":    return False

        for a in action.masterPoints2Count:
            flag = flag and (action.masterPoints2Count[a] <= hand_cards.cards[a])
        for a in action.slavePoints2Count:
            flag = flag and (action.slavePoints2Count[a] <= hand_cards.cards[a])
        return flag


    @classmethod
    def extractMasterCards(cls, hand_cards, pattern):
        """

        Args:
            hand_cards:
            pattern:

        Returns:

        """
        is_straight = pattern[3]
        cardss = []
        ss = []

        numPoint = pattern[2]
        if numPoint <= 0:
            return cardss
        count = pattern[1]/numPoint

        if is_straight == 1:
            c = 0
            for i in range(11, -1, -1):
                if hand_cards.cards[i] >= count:
                    c += 1
                else:
                    c = 0

                if c >= numPoint:
                    ss.append(range(i, i + numPoint))
        else:
            candidates = []
            for c in range(len(hand_cards.cards)):
                if hand_cards.cards[c] >= count:
                    candidates.append(c)
            if len(candidates) < numPoint:
                return []
            ss = list(itertools.combinations(candidates, numPoint))

        for set1 in ss:
            s = []
            for c in set1:
                for i in range(count):
                    s.append(c)
            s.sort()
            cardss.append(s)

        return cardss

    @classmethod
    def extractSlaveCards(cls, hand_cards, used_cards, pattern):
        """

        Args:
            hand_cards:
            used_cards:
            pattern:

        Returns:

        """
        used = [0 for i in range(15)]
        for p in used_cards:
            used[p] += 1

        numMaster = pattern[1]
        numMasterPoint = pattern[2]
        numSlave = pattern[4]

        candidates = []
        res1 = []
        res = []

        if numMaster / numMasterPoint == 3:
            if numSlave / numMasterPoint == 1:  # single
                for c in range(len(hand_cards.cards)):
                    for i in range(hand_cards.cards[c] - used[c]):
                        candidates.append(c)
                if len(candidates) >= numSlave:
                    res1 = list(set(list(itertools.combinations(candidates, numSlave))))
                for sCard in res1:  res.append([x for x in sCard])

            elif numSlave / numMasterPoint == 2:  # pair
                for c in range(len(hand_cards.cards)):
                    for i in range ((hand_cards.cards[c] - used[c])/2) :
                        candidates.append(c)
                if len(candidates) >= numSlave / 2:
                    res1 = list(set(list(itertools.combinations(candidates, int(numSlave / 2)))))
                for sCard in res1:
                    tmp = [x for x in sCard]
                    tmp.extend([x for x in sCard])
                    res.append(tmp)

        elif numMaster / numMasterPoint == 4:

            if numSlave / numMasterPoint == 2:  # single
                for c in range(len(hand_cards.cards)):
                    for i in range(hand_cards.cards[c] - used[c]):
                        candidates.append(c)
                if len(candidates) >= numSlave:
                    res1 = list(set(list(itertools.combinations(candidates, numSlave))))
                for sCard in res1:  res.append([x for x in sCard])


            elif numSlave / numMasterPoint == 4:  # pair
                for c in range(len(hand_cards.cards)):
                    for i in range((hand_cards.cards[c] - used[c])/2):
                        candidates.append(c)
                if len(candidates) >= numSlave / 2:
                    res1 = list(set(list(itertools.combinations(candidates, int(numSlave / 2)))))
                for sCard in res1:
                    tmp = [x for x in sCard]
                    tmp.extend([x for x in sCard])
                    res.append(tmp)

        return res


    @classmethod
    def action_priority(cls,action1, action2):
        """

        Args:
            action1:
            action2:

        Returns:

        """
        count1 = action1.pattern[1] / action1.pattern[2]
        count2 = action2.pattern[1] / action2.pattern[2]
        if count1 != count2:
            return count1 - count2

        numMaster1 = action1.pattern[1]
        numMaster2 = action2.pattern[2]
        if numMaster1 != numMaster2:
            return numMaster1  - numMaster2

        if action1.maxMasterPoint != action2.maxMasterPoint:
            return action1.maxMasterPoint - action2.maxMasterPoint

        raise ValueError("can't compare priorities of %s and %s "%(action1.key,action2))


    @classmethod
    def available_actions_generate_all(cls):
        """

        Returns:

        """
        public_state = DouDiZhuPublicState()
        person_state = DouDiZhuPersonState()
        public_state.is_response    = False
        person_state.hand_cards     = DouDiZhuHandCards("")
        for i in range(13):
            for j in range(4):
                person_state.hand_cards.add_cards(DouDiZhuActionElement.rank_to_str[i])
        person_state.hand_cards.add_cards(DouDiZhuActionElement.rank_to_str[DouDiZhuActionElement.r])
        person_state.hand_cards.add_cards(DouDiZhuActionElement.rank_to_str[DouDiZhuActionElement.R])
        actions = dict()


        patterns = []
        if public_state.phase == 0:
            patterns.append(AllPatterns["i_cheat"])
            patterns.append(AllPatterns["i_bid"])
        else:
            if public_state.is_response == False:
                for p in AllPatterns:
                    if p != "i_cheat" and p != "i_invalid":
                        patterns.append(AllPatterns[p])
            else:
                patterns.append(public_state.license_action.pattern)
                if public_state.license_action.pattern[6] == 1:
                    patterns.append(AllPatterns["p_4_1_0_0_0"])  # rank = 10
                    patterns.append(AllPatterns["x_rocket"])  # rank = 100
                if public_state.license_action.pattern[6] == 10:
                    patterns.append(AllPatterns["x_rocket"])  # rank = 100
                patterns.append(AllPatterns["i_cheat"])


        actions = dict()

        for pattern in patterns:
            numMaster = pattern[1]
            numMasterPoint = pattern[2]
            isStraight = pattern[3]
            numSlave = pattern[4]
            MasterCount = -1
            SlaveCount = -1

            if numMaster > 0:
                MasterCount = int(numMaster / numMasterPoint)

            if "i_invalid" == pattern[0]:
                continue

            if "i_cheat" == pattern[0]:
                action_key = DouDiZhuPokerAction.master_slave_cards_to_key([DouDiZhuActionElement.cheat], [])
                action     = DouDiZhuPokerAction([DouDiZhuActionElement.cheat], [])
                if action_key in actions:
                    if cls.action_priority(action, actions[action_key]) > 0:
                        actions[action_key] = action
                else:
                    actions[action_key] = action

                continue

            if "i_bid" == pattern[0]:
                action_key = DouDiZhuPokerAction.master_slave_cards_to_key([DouDiZhuActionElement.bid], [])
                action = DouDiZhuPokerAction([DouDiZhuActionElement.bid], [])
                if action_key in actions:
                    if cls.action_priority(action, actions[action_key]) > 0:
                        actions[action_key] = action
                else:
                    actions[action_key] = action
                continue

            if pattern[0] == "x_rocket":
                if person_state.hand_cards.cards[DouDiZhuActionElement.r] == 1 and \
                                person_state.hand_cards.cards[DouDiZhuActionElement.R] == 1:
                    action_key  = DouDiZhuPokerAction.master_slave_cards_to_key([DouDiZhuActionElement.r, DouDiZhuActionElement.R], [])
                    action = DouDiZhuPokerAction([DouDiZhuActionElement.r, DouDiZhuActionElement.R], [])
                    if action_key in actions:
                        if cls.action_priority(action, actions[action_key]) > 0:
                            actions[action_key] = action
                    else:
                        actions[action_key] = action
                continue

            if pattern[1] + pattern[4] > person_state.hand_cards.num_cards:
                continue
            sum1 = 0

            for count in range(MasterCount, 5, 1):
                sum1 += person_state.hand_cards.count2num[count]
            if sum1 < numMasterPoint:
                continue

            ### action with cards
            mCardss = []
            mCardss = DouDiZhuPokerEnv.extractMasterCards(person_state.hand_cards,  pattern)

            for mCards in mCardss:
                if numSlave == 0:
                    action_key   = DouDiZhuPokerAction.master_slave_cards_to_key(mCards, [])
                    action = DouDiZhuPokerAction(mCards, [])
                    if action_key in actions:
                        if cls.action_priority(action, actions[action_key]) > 0:
                            actions[action_key] = action
                    else:
                        actions[action_key] = action
                    continue

                sCardss = DouDiZhuPokerEnv.extractSlaveCards(person_state.hand_cards, mCards, pattern)
                for sCards in sCardss:
                    action_key  = DouDiZhuPokerAction.master_slave_cards_to_key(mCards, sCards)
                    action = DouDiZhuPokerAction(mCards, sCards)
                    if action_key in actions:
                        if cls.action_priority(action, actions[action_key]) > 0:
                            actions[action_key] = action
                    else:
                        actions[action_key] = action
        return actions
