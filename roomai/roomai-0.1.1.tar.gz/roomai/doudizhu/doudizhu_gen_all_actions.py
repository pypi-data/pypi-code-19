#!/bin/python

import roomai.doudizhu

actions = roomai.doudizhu.DouDiZhuPokerEnv.available_actions_generate_all()
for action_key in actions:
    print action_key+"\t"+ \
          ",".join([str(s) for s in actions[action_key].masterCards])+"\t"+\
          ",".join([str(s) for s in actions[action_key].slaveCards])+"\t" +\
          actions[action_key].pattern[0]
action = roomai.doudizhu.DouDiZhuPokerAction([roomai.doudizhu.DouDiZhuActionElement.cheat],[])
print action.key + "\t" + \
      ",".join([str(s) for s in action.masterCards]) + "\t" + \
      ",".join([str(s) for s in action.slaveCards]) + "\t" + \
      action.pattern[0]

action = roomai.doudizhu.DouDiZhuPokerAction([roomai.doudizhu.DouDiZhuActionElement.bid],[])
print action.key + "\t" + \
      ",".join([str(s) for s in action.masterCards]) + "\t" + \
      ",".join([str(s) for s in action.slaveCards]) + "\t" + \
      action.pattern[0]

