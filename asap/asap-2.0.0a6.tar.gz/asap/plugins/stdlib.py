
from asap.core import api

import sys
import random
import re
import logging

def strIfRequired(inp):
  '''
  convert an input to a string (if it is not yet)
  (warn if conversion was necessary)
  '''
  if isinstance(inp,str):
    return inp
  else:
    if __debug__:
      logging.warning("converted non-string input '{}'".format(repr(inp)))
    return str(inp)

def stripQuotes(inputs):
  '''
  remove outside quotes for all inputs
  return True, inputs' if anything was stripped,
  return False, inputs' otherwise
  '''
  changed = False
  out = []
  for i in inputs:
    i = strIfRequired(i)
    if i[0] == '"' and i[-1] == '"':
      changed = True
      out.append(i[1:-1])
    else:
      out.append(i)
  return changed, out

def conditionalQuote(quote, inp):
  if quote:
    return '"'+inp+'"'
  else:
    return inp

rCident = re.compile(r'[a-z_][A-Z0-9a-z_]*')
def quoteIfRequired(inp):
  if inp[0] != '"' and not rCident.match(inp):
    return '"'+inp+'"'
  else:
    return inp

class ChopExternal(api.External):
  '''
  remove last character of input string
  input: string
  output: string or nothing (if input empty)
  '''
  @property
  def interface(self):
    # one input, one output
    return ('chop',1,1,1)
  def query(self, einput):
    assert(len(einput.inputs) == 1)
    quoted, instrs = stripQuotes(einput.inputs)
    instr = instrs[0]
    if len(instr) == 0:
      return []
    else:
      out = conditionalQuote(quoted, instr[:-1])
      return [(api.Term(out),)]

class ConcatExternal(api.External):
  '''
  concatenate inputs
  output quoted string if one input was quoted string
  output term if no input was quoted string
  '''
  @property
  def interface(self):
    # at least 2 inputs, one output
    return ('concat',99,2,1)
  def query(self, einput):
    if __debug__:
      logging.debug("concat called with {}".format(repr(einput.inputs)))
    quoted, inputs = stripQuotes([str(i) for i in einput.inputs])
    if __debug__:
      logging.debug("concat called with {} {}".format(repr(quoted),repr(inputs)))
    out = conditionalQuote(quoted, ''.join(inputs))
    return [ (api.Term(out),) ]

#TODO make concat/chop always return strings

class RandomExternal(api.External):
  '''
  return random integer within given bounds
  input: lower, upper bound (int)
  output: random integer within bounds
  '''
  @property
  def interface(self):
    # 2 inputs, 1 output
    return ('random',2,2,1)
  def query(self, einput):
    assert(len(einput.inputs) == 2)
    #assert(isinstance(einput.inputs[0], int) and isinstance(einput.inputs[1], int))
    # convert and if this conversion fails we will get an exception anyways
    lower, upper = int(einput.inputs[0]), int(einput.inputs[1])
    out = random.randint(lower, upper)
    return [(api.Term(out),)]

class Plugin(api.ExternalAPI):
  def externals(self):
    return [ChopExternal(), ConcatExternal(), RandomExternal()]

