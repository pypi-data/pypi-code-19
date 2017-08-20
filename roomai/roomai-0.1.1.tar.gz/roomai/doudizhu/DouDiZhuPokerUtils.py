#!/bin/python
#coding:utf-8

import os
import roomai.common
import copy
import itertools



'''
class Utils:
    gen_allactions = False



    @classmethod
    def lookup_action(cls, masterCards, slaveCards):
        masterCards.sort()
        slaveCards.sort()

        key_int = (masterCards + slaveCards)
        key_str = []
        for i in key_int:
            key_str.append(DouDiZhuActionElement.rank_to_str[i])
        key_str.sort()
        key = "".join(key_str)

        if cls.gen_allactions == True:
            return key, DouDiZhuPokerAction(masterCards, slaveCards)

        if key in AllActions:
            return key, AllActions[key]
        else:
            raise Exception(key + "is not in AllActions")

    @classmethod
    def lookup_action_by_key(cls, key):
        if key in AllActions:
            return key, AllActions[key]
        else:
            raise Exception(key + "is not in AllActions")

    @classmethod
    def candidate_actions(cls, hand_cards, public_state):

        patterns = []
        if public_state.phase == PhaseSpace.bid:
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
                key, action = cls.lookup_action([DouDiZhuActionElement.cheat], [])
                if cls.is_action_valid(hand_cards, public_state, action) == True:
                    actions[key] = action
                continue

            if "i_bid" == pattern[0]:
                key, action = cls.lookup_action([DouDiZhuActionElement.bid], [])
                if cls.is_action_valid(hand_cards, public_state, action) == True:
                    actions[key] = action
                continue

            if pattern[0] == "x_rocket":
                if hand_cards.cards[DouDiZhuActionElement.r] == 1 and \
                                hand_cards.cards[DouDiZhuActionElement.R] == 1:
                    key, action = cls.lookup_action([DouDiZhuActionElement.r, DouDiZhuActionElement.R], [])
                    if cls.is_action_valid(hand_cards, public_state, action) == True:
                        actions[key] = action
                continue

            if pattern[1] + pattern[4] > hand_cards.num_cards:
                continue
            sum1 = 0

            for count in range(MasterCount, 5, 1):
                sum1 += hand_cards.count2num[count]
            if sum1 < numMasterPoint:
                continue

            ### action with cards
            mCardss = []
            mCardss = Utils.extractMasterCards(hand_cards, numMasterPoint, MasterCount, pattern)

            for mCards in mCardss:
                if numSlave == 0:
                    key, action = cls.lookup_action(mCards, [])
                    if cls.is_action_valid(hand_cards, public_state, action) == True:
                        actions[key] = action
                    continue

                sCardss = Utils.extractSlaveCards(hand_cards, numSlave, mCards, pattern)
                for sCards in sCardss:
                    key, action = cls.lookup_action(mCards, sCards)
                    if cls.is_action_valid(hand_cards, public_state, action) == True:
                        actions[key] = action
        return actions


'''
