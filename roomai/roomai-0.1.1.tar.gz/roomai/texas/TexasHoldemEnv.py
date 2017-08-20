#!/bin/python
#coding:utf-8

import random
import copy
import roomai.common
import roomai
import logging

from roomai.common import Info
from TexasHoldemUtil import *


class TexasHoldemEnv(roomai.common.AbstractEnv):
    """
    """

    @classmethod
    def check_initialization_configuration(cls, env):
        """

        Args:
            env:

        Returns:

        """
        if len(env.chips) != env.num_players:
            raise ValueError("len(env.chips)%d != env.num_players%d" % (len(env.chips), env.num_players))

        if env.num_players * 7 > 52:
            raise ValueError("env.num_players * 5 must be less than 51, now env.num_players = %d" % (env.num_players))

        return True

    #@override
    def init(self, params = dict()):
        """

        Args:
            params:

        Returns:

        """
        self.logger         = roomai.get_logger()

        if "num_players" in params:
            self.num_players = params["num_players"]
        else:
            self.num_players = 3

        if "dealer_id" in params:
            self.dealer_id = params["dealer_id"]
        else:
            self.dealer_id = int(random.random() * self.num_players)

        if "chips" in params:
            self.chips     = params["chips"]
        else:
            self.chips     = [1000 for i in range(self.num_players)]

        if "big_blind_bet" in params:
            self.big_blind_bet = params["big_blind_bet"]
        else:
            self.big_blind_bet = 10

        if "allcards" in params:
            self.allcards = [c.__deepcopy__() for c in params["allcards"]]
        else:
            self.allcards = []
            for i in xrange(13):
                for j in xrange(4):
                    self.allcards.append(roomai.common.PokerCard(i, j))
            random.shuffle(self.allcards)

        if "record_history" in params:
            self.record_history = params["record_history"]
        else:
            self.record_history = False


        self.check_initialization_configuration(self)

        hand_cards       = []
        for i in xrange(self.num_players):
              hand_cards.append(self.allcards[i*2:(i+1)*2])
        keep_cards   = self.allcards[self.num_players*2:self.num_players*2+5]

        ## public info
        small = (self.dealer_id + 1) % self.num_players
        big   = (self.dealer_id + 2) % self.num_players

        self.public_state                       = TexasHoldemPublicState()
        self.public_state.num_players           = self.num_players
        self.public_state.dealer_id             = self.dealer_id
        self.public_state.big_blind_bet         = self.big_blind_bet
        self.public_state.raise_account         = self.big_blind_bet

        self.public_state.is_fold               = [False for i in xrange(self.num_players)]
        self.public_state.num_quit              = 0
        self.public_state.is_allin              = [False for i in xrange(self.num_players)]
        self.public_state.num_allin             = 0
        self.public_state.is_needed_to_action   = [True for i in xrange(self.num_players)]
        self.public_state.num_needed_to_action  = self.public_state.num_players

        self.public_state.bets                  = [0 for i in xrange(self.num_players)]
        self.public_state.chips                 = self.chips
        self.public_state.stage                 = StageSpace.firstStage
        self.public_state.turn                  = (big+1)%self.public_state.num_players
        self.public_state.public_cards          = []

        self.public_state.previous_id           = None
        self.public_state.previous_action       = None

        if self.public_state.chips[big] > self.big_blind_bet:
            self.public_state.chips[big] -= self.big_blind_bet
            self.public_state.bets[big]  += self.big_blind_bet
        else:
            self.public_state.bets[big]     = self.public_state.chips[big]
            self.public_state.chips[big]    = 0
            self.public_state.is_allin[big] = True
            self.public_state.num_allin    += 1
        self.public_state.max_bet_sofar     = self.public_state.bets[big]
        self.public_state.raise_account = self.big_blind_bet

        if self.public_state.chips[small] > self.big_blind_bet / 2:
            self.public_state.chips[small] -= self.big_blind_bet /2
            self.public_state.bets[small]  += self.big_blind_bet /2
        else:
            self.public_state.bets[small]     = self.public_state.chips[small]
            self.public_state.chips[small]    = 0
            self.public_state.is_allin[small] = True
            self.public_state.num_allin      += 1

        self.public_state.is_terminal         = False
        self.public_state.scores              = None

        # private info
        self.private_state = TexasHoldemPrivateState()
        self.private_state.hand_cards       = [[] for i in xrange(self.num_players)]
        for i in xrange(self.num_players):
            self.private_state.hand_cards[i]  = [hand_cards[i][j].__deepcopy__() for j in xrange(len(hand_cards[i]))]
        self.private_state.keep_cards         = [keep_cards[i].__deepcopy__() for i in xrange(len(keep_cards))]

        ## person info
        self.person_states                      = [TexasHoldemPersonState() for i in xrange(self.num_players)]
        for i in xrange(self.num_players):
            self.person_states[i].id = i
            self.person_states[i].hand_cards = [hand_cards[i][j].__deepcopy__() for j in xrange(len(hand_cards[i]))]
        self.person_states[self.public_state.turn].available_actions = self.available_actions(self.public_state, self.person_states[self.public_state.turn])

        self.__gen_history__()
        infos = self.__gen_infos__()

        if self.logger.level <= logging.DEBUG:
            self.logger.debug("TexasHoldemEnv.init: num_players = %d, dealer_id = %d, chip = %d, big_blind_bet = %d"%(\
                self.public_state.num_players,\
                self.public_state.dealer_id,\
                self.public_state.chips[0],\
                self.public_state.big_blind_bet
            ))

        return infos, self.public_state, self.person_states, self.private_state

    ## we need ensure the action is valid
    #@Overide
    def forward(self, action):
        """
        Args:
            action: 

        Raises:
            None: throw ValueError when the action is invalid at this time
        """
        pu         = self.public_state
        pe         = self.person_states
        pr         = self.private_state

        if not self.is_action_valid(action, pu, pe[pu.turn]):
            self.logger.critical("action=%s is invalid" % (action.key))
            raise ValueError("action=%s is invalid" % (action.key))


        if action.option == TexasHoldemAction.Fold:
            self.action_fold(action)
        elif action.option == TexasHoldemAction.Check:
            self.action_check(action)
        elif action.option == TexasHoldemAction.Call:
            self.action_call(action)
        elif action.option == TexasHoldemAction.Raise:
            self.action_raise(action)
        elif action.option == TexasHoldemAction.AllIn:
            self.action_allin(action)
        else:
            raise Exception("action.option(%s) not in [Fold, Check, Call, Raise, AllIn]"%(action.option))
        pu.previous_id     = pu.turn
        pu.previous_action = action
        pu.is_terminal     = False
        pu.scores          = None

        # computing_score
        if TexasHoldemEnv.is_compute_scores(self.public_state):
            ## need showdown
            pu.public_cards = pr.keep_cards[0:5]
            pu.is_terminal  = True
            pu.scores       = self.compute_scores()


        # enter into the next stage
        elif TexasHoldemEnv.is_nextround(self.public_state):
            add_cards = []
            if pu.stage == StageSpace.firstStage:   add_cards = pr.keep_cards[0:3]
            if pu.stage == StageSpace.secondStage:  add_cards = [pr.keep_cards[3]]
            if pu.stage == StageSpace.thirdStage:   add_cards = [pr.keep_cards[4]]

            pu.public_cards.extend(add_cards)
            pu.stage                      = pu.stage + 1

            pu.num_needed_to_action       = 0
            pu.is_needed_to_action        = [False for i in xrange(pu.num_players)]
            for i in xrange(pu.num_players):
                if pu.is_fold[i] != True and pu.is_allin[i] != True:
                    pu.is_needed_to_action[i]      = True
                    pu.num_needed_to_action       += 1

            pu.turn                                             = pu.dealer_id
            pu.turn                                             = self.next_player(pu)
            pe[self.public_state.previous_id].available_actions = dict()
            pe[self.public_state.turn].available_actions        = self.available_actions(self.public_state, self.person_states[self.public_state.turn])

        ##normal
        else:
            pu.turn                                                             = self.next_player(pu)
            self.person_states[self.public_state.previous_id].available_actions = dict()
            self.person_states[self.public_state.turn].available_actions        = self.available_actions(self.public_state, self.person_states[self.public_state.turn])


        if self.logger.level <= logging.DEBUG:
            self.logger.debug("TexasHoldemEnv.forward: num_quit+num_allin = %d+%d = %d, action = %s, stage = %d"%(\
                self.public_state.num_quit,\
                self.public_state.num_allin,\
                self.public_state.num_quit + self.public_state.num_allin,\
                action.key,\
                self.public_state.stage\
            ))

        self.__gen_history__()
        infos = self.__gen_infos__()
        return infos, self.public_state, self.person_states, self.private_state

    #override
    @classmethod
    def compete(cls, env, players):
        """

        Args:
            env:
            players:

        Returns:

        """

        total_scores       = [0    for i in xrange(len(players))]
        total_count        = 1000


        for count in xrange(total_count):

            chips          = [(1000 + int(random.random() * 200)) for i in range(len(players))]
            num_players    = len(players)
            dealer_id      = int(random.random() * len(players))
            big_blind_bet  = 50

            infos, public, persons, private = env.init({"chips":chips,
                                                        "num_players":num_players,
                                                        "dealer_id":dealer_id,
                                                        "big_blind_bet":big_blind_bet})
            for i in xrange(len(players)):
                players[i].receive_info(infos[i])
            while public.is_terminal == False:
                turn = public.turn
                action = players[turn].take_action()
                #print len(infos[turn].person_state.available_actions),action.key(),turn
                infos, public, persons, private = env.forward(action)
                for i in xrange(len(players)):
                    players[i].receive_info(infos[i])

            for i in xrange(len(players)):
                players[i].receive_info(infos[i])
                total_scores[i] += public.scores[i]

            '''
            if count < 1000:
                print count,public.dealer_id,public.scores,public.stage
                for i in xrange(public.num_players):
                    for j in xrange(len(private.hand_cards[i])):
                        print private.hand_cards[i][j].key,
                    print ""
                print len(public.public_cards)
                for j in xrange(len(public.public_cards)):
                    print public.public_cards[j].key,
                print ""
                for i in xrange(public.num_players):
                    x = cls.cards2pattern(private.hand_cards[i], public.public_cards)
                    print x[0],x[5]
            '''

            if (count + 1)%500 == 0:
                tmp_scores = [0 for i in xrange(len(total_scores))]
                for i in xrange(len(total_scores)):
                    tmp_scores[i] = total_scores[i] / (count+1)
                roomai.get_logger().info("TexasHoldem completes %d competitions, scores=%s"%(count+1, ",".join([str(i) for i in tmp_scores])))

        for i in xrange(len(total_scores)):
            total_scores[i] /= 1.0 * total_count

        return total_scores


    def compute_scores(self):
        """
        Returns:
            a score array
        """
        pu = self.public_state
        pr = self.private_state

        ## compute score before showdown, the winner takes all
        if pu.num_players  ==  pu.num_quit + 1:
            scores = [0 for i in xrange(pu.num_players)]
            for i in xrange(pu.num_players):
                if pu.is_fold[i] == False:
                    scores[i] = sum(pu.bets)
                    break

        ## compute score after showdown
        else:
            scores                = [0 for i in xrange(pu.num_players)]
            playerid_pattern_bets = [] #for not_quit players
            for i in xrange(pu.num_players):
                if pu.is_fold[i] == True: continue
                hand_pattern = self.cards2pattern(pr.hand_cards[i], pr.keep_cards)
                playerid_pattern_bets.append((i,hand_pattern,pu.bets[i]))
            playerid_pattern_bets.sort(key=lambda x:x[1], cmp=self.compare_patterns)

            pot_line = 0
            previous = None
            tmp_playerid_pattern_bets      = []
            for i in xrange(len(playerid_pattern_bets)-1,-1,-1):
                if previous == None:
                    tmp_playerid_pattern_bets.append(playerid_pattern_bets[i])
                    previous = playerid_pattern_bets[i]
                elif self.compare_patterns(playerid_pattern_bets[i][1], previous[1]) == 0:
                    tmp_playerid_pattern_bets.append(playerid_pattern_bets[i])
                    previous = playerid_pattern_bets[i]
                else:
                    tmp_playerid_pattern_bets.sort(key = lambda x:x[2])
                    for k in xrange(len(tmp_playerid_pattern_bets)):
                        num1          = len(tmp_playerid_pattern_bets) - k
                        sum1          = 0
                        max_win_score = pu.bets[tmp_playerid_pattern_bets[k][0]]
                        for p in xrange(pu.num_players):
                            sum1      += min(max(0, pu.bets[p] - pot_line), max_win_score)
                        for p in xrange(k, len(tmp_playerid_pattern_bets)):
                            scores[tmp_playerid_pattern_bets[p][0]] += sum1 / num1
                        scores[pu.dealer_id] += sum1 % num1
                        if pot_line <= max_win_score:
                            pot_line = max_win_score
                    tmp_playerid_pattern_bets = []
                    tmp_playerid_pattern_bets.append(playerid_pattern_bets[i])
                    previous = playerid_pattern_bets[i]


            if len(tmp_playerid_pattern_bets) > 0:
                tmp_playerid_pattern_bets.sort(key = lambda  x:x[2])
                for i in xrange(len(tmp_playerid_pattern_bets)):
                    num1 = len(tmp_playerid_pattern_bets) - i
                    sum1 = 0
                    max_win_score = pu.bets[tmp_playerid_pattern_bets[i][0]]
                    for p in xrange(pu.num_players):
                        sum1 += min(max(0, pu.bets[p] - pot_line), max_win_score)
                    for p in xrange(i, len(tmp_playerid_pattern_bets)):
                        scores[tmp_playerid_pattern_bets[p][0]] += sum1 / num1
                    scores[pu.dealer_id] += sum1 % num1
                    if pot_line <= max_win_score: pot_line = max_win_score

        for p in xrange(pu.num_players):
            pu.chips[p] += scores[p]
            scores[p]   -= pu.bets[p]
        for p in xrange(pu.num_players):
            scores[p]   /= pu.big_blind_bet * 1.0
        return scores


    def action_fold(self, action):
        """

        Args:
            action:
        """
        pu = self.public_state
        pu.is_fold[pu.turn]             = True
        pu.num_quit                    += 1

        pu.is_needed_to_action[pu.turn] = False
        pu.num_needed_to_action        -= 1

    def action_check(self, action):
        """

        Args:
            action:
        """
        pu = self.public_state
        pu.is_needed_to_action[pu.turn] = False
        pu.num_needed_to_action        -= 1

    def action_call(self, action):
        """

        Args:
            action:
        """
        pu = self.public_state
        pu.chips[pu.turn] -= action.price
        pu.bets[pu.turn]  += action.price
        pu.is_needed_to_action[pu.turn] = False
        pu.num_needed_to_action        -= 1

    def action_raise(self, action):
        """

        Args:
            action:
        """
        pu = self.public_state


        pu.raise_account   = action.price + pu.bets[pu.turn] - pu.max_bet_sofar
        pu.chips[pu.turn] -= action.price
        pu.bets[pu.turn]  += action.price
        pu.max_bet_sofar   = pu.bets[pu.turn]

        pu.is_needed_to_action[pu.turn] = False
        pu.num_needed_to_action        -= 1
        p = (pu.turn + 1)%pu.num_players
        while p != pu.turn:
            if pu.is_allin[p] == False and pu.is_fold[p] == False and pu.is_needed_to_action[p] == False:
                pu.num_needed_to_action   += 1
                pu.is_needed_to_action[p]  = True
            p = (p + 1) % pu.num_players


    def action_allin(self, action):
        """

        Args:
            action:
        """
        pu = self.public_state

        pu.is_allin[pu.turn]   = True
        pu.num_allin          += 1

        pu.bets[pu.turn]      += action.price
        pu.chips[pu.turn]      = 0

        pu.is_needed_to_action[pu.turn] = False
        pu.num_needed_to_action        -= 1
        if pu.bets[pu.turn] > pu.max_bet_sofar:
            pu.max_bet_sofar = pu.bets[pu.turn]
            p = (pu.turn + 1) % pu.num_players
            while p != pu.turn:
                if pu.is_allin[p] == False and pu.is_fold[p] == False and pu.is_needed_to_action[p] == False:
                    pu.num_needed_to_action  += 1
                    pu.is_needed_to_action[p] = True
                p = (p + 1) % pu.num_players

            pu.max_bet_sofar = pu.bets[pu.turn]

#####################################Utils Function ##############################

    @classmethod
    def next_player(self, pu):
        """

        Args:
            pu:

        Returns:

        """
        i = pu.turn
        if pu.num_needed_to_action == 0:
            return -1

        p = (i+1)%pu.num_players
        while pu.is_needed_to_action[p] == False:
            p = (p+1)%pu.num_players
        return p

    @classmethod
    def is_compute_scores(self, pu):
        '''
        :return: 
        A boolean variable indicates whether is it time to compute scores
        '''

        if pu.num_players == pu.num_quit + 1:
            return True

        # below need showdown

        if pu.num_players <=  pu.num_quit + pu.num_allin +1 and pu.num_needed_to_action == 0:
            return True

        if pu.stage == StageSpace.fourthStage and self.is_nextround(pu):
            return True

        return False

    @classmethod
    def is_nextround(self, public_state):
        '''
        :return: 
        A boolean variable indicates whether is it time to enter the next stage
        '''
        return public_state.num_needed_to_action == 0

    @classmethod
    def cards2pattern(cls, hand_cards, remaining_cards):
        """

        Args:
            hand_cards:
            remaining_cards:

        Returns:

        """
        pointrank2cards = dict()
        for c in hand_cards + remaining_cards:
            if c.get_point_rank() in pointrank2cards:
                pointrank2cards[c.get_point_rank()].append(c)
            else:
                pointrank2cards[c.get_point_rank()] = [c]
        for p in pointrank2cards:
            pointrank2cards[p].sort(roomai.common.PokerCard.compare)

        suitrank2cards = dict()
        for c in hand_cards + remaining_cards:
            if c.get_suit_rank() in suitrank2cards:
                suitrank2cards[c.get_suit_rank()].append(c)
            else:
                suitrank2cards[c.get_suit_rank()] = [c]
        for s in suitrank2cards:
            suitrank2cards[s].sort(roomai.common.PokerCard.compare)

        num2point = [[], [], [], [], []]
        for p in pointrank2cards:
            num = len(pointrank2cards[p])
            num2point[num].append(p)
        for i in xrange(5):
            num2point[num].sort()

        sorted_point = []
        for p in pointrank2cards:
            sorted_point.append(p)
        sorted_point.sort()

        ##straight_samesuit
        for s in suitrank2cards:
            if len(suitrank2cards[s]) >= 5:
                numStraight = 1
                for i in xrange(len(suitrank2cards[s]) - 2, -1, -1):
                    if suitrank2cards[s][i].get_point_rank() == suitrank2cards[s][i + 1].get_point_rank() - 1:
                        numStraight += 1
                    else:
                        numStraight = 1

                    if numStraight == 5:
                        pattern = AllCardsPattern["Straight_SameSuit"]
                        pattern[6] = suitrank2cards[s][i:i + 5]
                        return pattern

        ##4_1
        if len(num2point[4]) > 0:
            p4 = num2point[4][0]
            p1 = -1
            for i in xrange(len(sorted_point) - 1, -1, -1):
                if sorted_point[i] != p4:
                    p1 = sorted_point[i]
                    break
            pattern = AllCardsPattern["4_1"]
            pattern[6] = pointrank2cards[p4][0:4]
            pattern[6].append(pointrank2cards[p1][0])
            return pattern

        ##3_2
        if len(num2point[3]) >= 1:
            pattern = AllCardsPattern["3_2"]

            if len(num2point[3]) == 2:
                p3 = num2point[3][1]
                pattern[6] = pointrank2cards[p3][0:3]
                p2 = num2point[3][0]
                pattern[6].append(pointrank2cards[p2][0])
                pattern[6].append(pointrank2cards[p2][1])
                return pattern

            if len(num2point[2]) >= 1:
                p3 = num2point[3][0]
                pattern[6] = pointrank2cards[p3][0:3]
                p2 = num2point[2][len(num2point[2]) - 1]
                pattern[6].append(pointrank2cards[p2][0])
                pattern[6].append(pointrank2cards[p2][1])
                return pattern

        ##SameSuit
        for s in suitrank2cards:
            if len(suitrank2cards[s]) >= 5:
                pattern = AllCardsPattern["SameSuit"]
                len1 = len(suitrank2cards[s])
                pattern[6] = suitrank2cards[s][len1 - 5:len1]
                return pattern

        ##Straight_DiffSuit
        numStraight = 1
        for idx in xrange(len(sorted_point) - 2, -1, -1):
            if sorted_point[idx] + 1 == sorted_point[idx]:
                numStraight += 1
            else:
                numStraight = 1

            if numStraight == 5:
                pattern = AllCardsPattern["Straight_DiffSuit"]
                for p in xrange(idx, idx + 5):
                    point = sorted_point[p]
                    pattern[6].append(pointrank2cards[point][0])
                return pattern

        ##3_1_1
        if len(num2point[3]) == 1:
            pattern = AllCardsPattern["3_1_1"]

            p3 = num2point[3][0]
            pattern[6] = pointrank2cards[p3][0:3]

            num = 0
            for i in xrange(len(sorted_point) - 1, -1, -1):
                p = sorted_point[i]
                if p != p3:
                    pattern[6].append(pointrank2cards[p][0])
                    num += 1
                if num == 2:    break
            return pattern

        ##2_2_1
        if len(num2point[2]) >= 2:
            pattern = AllCardsPattern["2_2_1"]
            p21 = num2point[2][len(num2point[2]) - 1]
            for c in pointrank2cards[p21]:
                pattern[6].append(c)
            p22 = num2point[2][len(num2point[2]) - 2]
            for c in pointrank2cards[p22]:
                pattern[6].append(c)

            flag = False
            for i in xrange(len(sorted_point) - 1, -1, -1):
                p = sorted_point[i]
                if p != p21 and p != p22:
                    c = pointrank2cards[p][0]
                    pattern[6].append(c)
                    flag = True
                if flag == True:    break;
            return pattern

        ##2_1_1_1
        if len(num2point[2]) == 1:
            pattern = AllCardsPattern["2_1_1_1"]
            p2 = num2point[2][0]
            pattern[6] = pointrank2cards[p2][0:2]
            num = 0
            for p in xrange(len(sorted_point) - 1, -1, -1):
                p1 = sorted_point[p]
                if p1 != p2:
                    pattern[6].append(pointrank2cards[p1][0])
                if num == 3:    break
            return pattern

        ##1_1_1_1_1
        pattern = AllCardsPattern["1_1_1_1_1"]
        count = 0
        for i in xrange(len(sorted_point) - 1, -1, -1):
            p = sorted_point[i]
            for c in pointrank2cards[p]:
                pattern[6].append(c)
                count += 1
                if count == 5: break
            if count == 5: break
        return pattern

    @classmethod
    def compare_handcards(cls, hand_card0, hand_card1, keep_cards):
        """

        Args:
            hand_card0:
            hand_card1:
            keep_cards:

        Returns:

        """
        pattern0 = TexasHoldemEnv.cards2pattern(hand_card0, keep_cards)
        pattern1 = TexasHoldemEnv.cards2pattern(hand_card1, keep_cards)

        diff = cls.compare_patterns(pattern0, pattern1)
        return diff

    @classmethod
    def compare_patterns(cls, p1, p2):
        """

        Args:
            p1:
            p2:

        Returns:

        """
        if p1[5] != p2[5]:
            return p1[5] - p2[5]
        else:
            for i in xrange(5):
                if p1[6][i] != p2[6][i]:
                    return p1[6][i] - p2[6][i]
            return 0

    @classmethod
    def available_actions(cls, public_state, person_state):
        """

        Args:
            public_state:
            person_state:

        Returns:

        """
        pu = public_state
        turn = pu.turn
        key_actions = dict()

        ## for fold
        action = TexasHoldemAction(TexasHoldemAction.Fold + "_0")
        if cls.is_action_valid(action,public_state, person_state):
            key_actions[action.key] = action

        ## for check
        if pu.bets[turn] == pu.max_bet_sofar:
            action = TexasHoldemAction(TexasHoldemAction.Check + "_0")
            if cls.is_action_valid(action, public_state, person_state):
                key_actions[action.key] = action

        ## for call
        if pu.bets[turn] != pu.max_bet_sofar and pu.chips[turn] > pu.max_bet_sofar - pu.bets[turn]:
            action = TexasHoldemAction(TexasHoldemAction.Call + "_%d" % (pu.max_bet_sofar - pu.bets[turn]))
            if cls.is_action_valid(action, public_state, person_state):
                key_actions[action.key] = action

        ## for raise
        if pu.bets[turn] != pu.max_bet_sofar and pu.chips[turn] > pu.max_bet_sofar - pu.bets[turn] + pu.raise_account:
            num = (pu.chips[turn] - (pu.max_bet_sofar - pu.bets[turn])) / pu.raise_account
            for i in xrange(1, num + 1):
                price = pu.max_bet_sofar - pu.bets[turn] + pu.raise_account * i
                if price == pu.chips[pu.turn]:  continue
                action = TexasHoldemAction(TexasHoldemAction.Raise + "_%d" % (price))
                if cls.is_action_valid(action, public_state, person_state):
                    key_actions[action.key] = action

        ## for all in
        action = TexasHoldemAction(TexasHoldemAction.AllIn + "_%d" % (pu.chips[turn]))
        if cls.is_action_valid(action, public_state, person_state):
            key_actions[action.key] = action

        return key_actions

    @classmethod
    def is_action_valid(cls, action, public_state, person_state):
        """

        Args:
            action:
            public_state:
            person_state:

        Returns:

        """
        pu = public_state

        if (not isinstance(public_state, TexasHoldemPublicState)) or (not isinstance(action, TexasHoldemAction)):
            return False

        if pu.is_allin[pu.turn] == True or pu.is_fold[pu.turn] == True:
            return False
        if pu.chips[pu.turn] == 0:
            return False

        if action.option == TexasHoldemAction.Fold:
            return True

        elif action.option == TexasHoldemAction.Check:
            if pu.bets[pu.turn] == pu.max_bet_sofar:
                return True
            else:
                return False

        elif action.option == TexasHoldemAction.Call:
            if action.price == pu.max_bet_sofar - pu.bets[pu.turn]:
                return True
            else:
                return False

        elif action.option == TexasHoldemAction.Raise:
            raise_account = action.price - (pu.max_bet_sofar - pu.bets[pu.turn])
            if raise_account == 0:    return False
            if raise_account % pu.raise_account == 0:
                return True
            else:
                return False
        elif action.option == TexasHoldemAction.AllIn:
            if action.price == pu.chips[pu.turn]:
                return True
            else:
                return False
        else:
            raise Exception("Invalid action.option" + action.option)

