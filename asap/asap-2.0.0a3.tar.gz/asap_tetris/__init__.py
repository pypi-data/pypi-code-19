
from asap.core import api

import math

class DelayFromLevelExternal(api.External):
  '''
  compute milliseconds for stone drop depending on game level (difficulty)
  input: level (int)
  output: milliseconds (int)
  '''
  def __init__(self):
    # if easiness is 1, game becomes more difficult very fast
    # the higher this number, the longer the game will take
    self.easiness = 5.0 #10.0
  @property
  def interface(self):
    # one mandatory input, one output
    return ('delayFromLevel',1,1,1)
  def query(self, einput):
    assert(len(einput.inputs) == 1)
    level = int(einput.inputs[0])
    delay_ms = int(1000.0*math.exp(-level / self.easiness))
    return [ (api.Term(delay_ms),) ]

class Plugin(api.ExternalAPI):
  def externals(self):
    return [DelayFromLevelExternal()]

