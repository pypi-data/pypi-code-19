#!/bin/python
import os
import roomai.common
import copy


#
#0, 1, 2, 3, ..., 7,  8, 9, 10, 11, 12, 13, 14
#^                ^   ^              ^       ^
#|                |   |              |       |
#3,               10, J, Q,  K,  A,  2,  r,  R
#

class DouDiZhuActionElement:
    """
    """
    str_to_rank  = {'3':0, '4':1, '5':2, '6':3, '7':4, '8':5, '9':6, 'T':7, 'J':8, 'Q':9, 'K':10, 'A':11, '2':12, 'r':13, 'R':14, 'x':15, 'b':16}
    # x means check, b means bid
    rank_to_str  = {0: '3', 1: '4', 2: '5', 3: '6', 4: '7', 5: '8', 6: '9', 7: 'T', 8: 'J', 9: 'Q', 10: 'K', 11: 'A', 12: '2', 13: 'r', 14: 'R', 15: 'x', 16: 'b'}
    three       = 0;
    four        = 1;
    five        = 2;
    six         = 3;
    seven       = 4;
    eight       = 5;
    night       = 6;
    ten         = 7;
    J           = 8;
    Q           = 9;
    K           = 10;
    A           = 11;
    two         = 12;
    r           = 13;
    R           = 14;
    cheat       = 15;
    bid         = 16;

    total_normal_cards = 15



class DouDiZhuPokerAction(roomai.common.AbstractAction):
    """
    """
    def __init__(self):
        """

        """
        pass

    def __init__(self, masterCards, slaveCards):
        """

        Args:
            masterCards:
            slaveCards:
        """
        self.__masterCards        = copy.deepcopy(masterCards)
        self.__slaveCards         = copy.deepcopy(slaveCards)

        self.__masterPoints2Count = None
        self.__slavePoints2Count  = None
        self.__isMasterStraight   = None
        self.__maxMasterPoint     = None
        self.__minMasterPoint     = None
        self.__pattern            = None

        self.action2pattern()
        self.__key = DouDiZhuPokerAction.master_slave_cards_to_key(masterCards, slaveCards)



    @property
    def key(self):  return self.__key
    @property
    def masterCards(self):  return self.__masterCards
    @property
    def slaveCards(self):   return self.__slaveCards
    @property
    def masterPoints2Count(self):   return self.__masterPoints2Count
    @property
    def slavePoints2Count(self):    return self.__slavePoints2Count
    @property
    def isMasterStraight(self):     return self.__isMasterStraight
    @property
    def maxMasterPoint(self):       return self.__maxMasterPoint
    @property
    def minMasterPoint(self):       return self.__minMasterPoint
    @property
    def pattern(self):              return self.__pattern

    @classmethod
    def lookup(cls, key):
        """

        Args:
            key:

        Returns:

        """
        return AllActions["".join(sorted(key))]

    @classmethod
    def master_slave_cards_to_key(cls, masterCards, slaveCards):
        """

        Args:
            masterCards:
            slaveCards:

        Returns:

        """
        key_int = (masterCards + slaveCards)
        key_str = []
        for key in key_int:
            key_str.append(DouDiZhuActionElement.rank_to_str[key])
        key_str.sort()
        return "".join(key_str)

    def action2pattern(self):
        """

        """

        self.__masterPoints2Count = dict()
        for c in self.__masterCards:
            if c in self.__masterPoints2Count:
                self.__masterPoints2Count[c] += 1
            else:
                self.__masterPoints2Count[c] = 1

        self.__slavePoints2Count = dict()
        for c in self.__slaveCards:
            if c in self.__slavePoints2Count:
                self.__slavePoints2Count[c] += 1
            else:
                self.__slavePoints2Count[c] = 1

        self.__isMasterStraight = 0
        num = 0
        for v in self.__masterPoints2Count:
            if (v + 1) in self.__masterPoints2Count and (v + 1) < DouDiZhuActionElement.two:
                num += 1
        if num == len(self.__masterPoints2Count) - 1 and len(self.__masterPoints2Count) != 1:
            self.__isMasterStraight = 1

        self.__maxMasterPoint = -1
        self.__minMasterPoint = 100
        for c in self.__masterPoints2Count:
            if self.__maxMasterPoint < c:
                self.__maxMasterPoint = c
            if self.__minMasterPoint > c:
                self.__minMasterPoint = c

        ########################
        ## action 2 pattern ####
        ########################


        # is cheat?
        if len(self.__masterCards) == 1 \
                and len(self.__slaveCards) == 0 \
                and self.__masterCards[0] == DouDiZhuActionElement.cheat:
            self.__pattern = AllPatterns["i_cheat"]

        # is roblord
        elif len(self.__masterCards) == 1 \
                and len(self.__slaveCards) == 0 \
                and self.__masterCards[0] == DouDiZhuActionElement.bid:
            self.__pattern = AllPatterns["i_bid"]

        # is twoKings
        elif len(self.__masterCards) == 2 \
                and len(self.__masterPoints2Count) == 2 \
                and len(self.__slaveCards) == 0 \
                and self.__masterCards[0] in [DouDiZhuActionElement.r, DouDiZhuActionElement.R] \
                and self.__masterCards[1] in [DouDiZhuActionElement.r, DouDiZhuActionElement.R]:
            self.__pattern = AllPatterns["x_rocket"]

        else:

            ## process masterCards
            masterPoints = self.__masterPoints2Count
            if len(masterPoints) > 0:
                count = masterPoints[self.__masterCards[0]]
                for c in masterPoints:
                    if masterPoints[c] != count:
                        self.__pattern = AllPatterns["i_invalid"]

            if self.__pattern == None:
                pattern = "p_%d_%d_%d_%d_%d" % (len(self.__masterCards), len(masterPoints), \
                                                self.__isMasterStraight, \
                                                len(self.__slaveCards), 0)

                if pattern in AllPatterns:
                    self.__pattern = AllPatterns[pattern]
                else:
                    self.__pattern = AllPatterns["i_invalid"]

    def __deepcopy__(self, memodict={}, newinstance = None):
        """

        Args:
            memodict:
            newinstance:

        Returns:

        """
        return self.lookup(self.key)



############## read data ################
AllPatterns = dict()
AllActions = dict()
import zipfile
def get_file(path):
    """

    Args:
        path:

    Returns:

    """
    if ".zip" in path:
        lines = path.split(".zip")
        zip1 = zipfile.ZipFile(lines[0] + ".zip")
        len1 = len(lines[1])
        path = lines[1][1:len1]
        return zip1.open(path)
    else:
        return open(path)
path = os.path.split(os.path.realpath(__file__))[0]
pattern_file = get_file(path + "/patterns.py")
for line in pattern_file:
    line = line.replace(" ", "").strip()
    line = line.split("#")[0]
    if len(line) == 0:  continue
    lines = line.split(",")
    for i in range(1, len(lines)):
        lines[i] = int(lines[i])
    AllPatterns[lines[0]] = lines
pattern_file.close()



action_file = get_file(path + "/actions.py")
for line in action_file:
    line = line.replace(" ", "").strip()
    lines = line.split("\t")
    m = [int(str1) for str1 in lines[1].split(",")]
    s = []
    if len(lines[2]) > 0:
        s = [int(str1) for str1 in lines[2].split(",")]
    action = DouDiZhuPokerAction(m, s)
    if action.key != lines[0] or action.pattern[0] != lines[3]:
        print lines
        raise ValueError("%s is wrong. The generated action has key(%s) and pattern(%s)"%(line, action.key,action.pattern[0]))


    AllActions[action.key] = action
action_file.close()



