#
# ASAP Answer Set Application Programming - ASAP Python API
#

#Copyright (c) 2015, Peter Schueller <peter.schuller@marmara.edu.tr>
#Copyright (c) 2015, Antonius Weinzierl <weinzierl@kr.tuwien.ac.at>
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
#
#1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#
#2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
#
#3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import time
import sys
import re
import logging

def debug(msg):
  # TODO replace below
  logging.debug(msg)

def warn(msg):
  # TODO replace below
  logging.warning(msg)

rCident = re.compile(r'[a-z_][A-Z0-9a-z_]*')

class Term:
  '''
  a term or atom in an interpretation
  '''
  # TODO maybe pull out of class and make module function
  @staticmethod
  def fromNestedTuple(nestedtuple):
    '''
    instantiate a term from a tuples containing tuples/strings/integers in any nesting level
    '''
    if not isinstance(nestedtuple,tuple) or len(nestedtuple) == 0:
      raise Exception("fromNestedTuple requires nonempty tuple as input (got {})".format(repr(nestedtuple)))
    if not isinstance(nestedtuple[0], (str,int)):
      raise Exception("fromNestedTuple requires int or string as first tuple element (got {})".format(repr(nestedtuple[0])))
    args = []
    for a in nestedtuple[1:]:
      if isinstance(a,int) or isinstance(a,str):
        args.append(Term(a))
      else:
        args.append(Term.fromNestedTuple(a))
    return Term(nestedtuple[0], tuple(args))
  def __init__(self,pred,args=[]):
    '''
    initialize term with predicate (str or int) and iterable arguments
    each argument is a Term
    '''
    if not isinstance(pred,str) and not isinstance(pred,int):
      raise Exception("Term must have str or int predicate (is '{}')".format(repr(pred)))
    if not isinstance(args,(list,tuple)):
      raise Exception("Term must have list or tuple as arguments (has '{}')".format(repr(args)))
    if isinstance(pred,int) and len(args) > 0:
      raise Exception("Term(int) '{}' cannot have arguments".format(pred))
    if isinstance(pred,str) and not ((pred[0] == '"') ^ (pred[-1] != '"')):
      raise Exception("Term(str) '{}' needs either opening AND closing quotes, or no quotes at all".format(pred))
    if isinstance(pred,str) and pred[0] != '"' and not rCident.match(pred):
      raise Exception("Term(str) '{}' must be CIDENT".format(pred))
    if not all([ (isinstance(arg,str) or isinstance(arg,int) or isinstance(arg,Term)) for arg in args]):
      raise Exception("Term must have Term arguments (has '{}')".format(','.join([repr(x) for x in args])))
    self.tupl = tuple([pred]+list(args))
  @property
  def pred(self):
    return self.tupl[0]
  @property
  def args(self):
    return self.tupl[1:]
  def as_tuple(self):
    # return internal tuple, it is read-only (and contains only Terms which are read-only)
    return self.tupl
  def __int__(self):
    if not isinstance(self.tupl[0],int):
      raise Exception("requested integer of api.Term '{}' which is not of type integer".format(pred))
    return self.tupl[0]
  def unquoted(self):
    # returns predicate constant or predicate string without quotes
    assert(len(self.tupl) == 1 and isinstance(self.pred,str))
    if self.pred[0] == '"' and self.pred[-1] == '"':
      return self.pred[1:-1]
    else:
      return self.pred
  def __hash__(self):
    return hash(self.tupl)
  def __str__(self):
    if len(self.tupl) == 1:
      return str(self.tupl[0])
    else:
      return '{}({})'.format(self.tupl[0], ','.join([str(x) for x in self.tupl[1:]]))
  def __repr__(self):
    if len(self.tupl) == 1:
      return 'Term({})'.format(self.tupl[0])
    else:
      return 'Term({}({}))'.format(self.tupl[0], ','.join([repr(x) for x in self.tupl[1:]]))

class Event:
  '''
  Event representation in ASAP
  '''
  firstEventTimestamp = time.time()
  def __init__(self, term):
    self.term = term
    self.timestamp = time.time() - Event.firstEventTimestamp
    #debug("constructed event "+str(self))
  def __str__(self):
    return "Event({},{})".format(self.term, self.timestamp)
  def __repr__(self):
    return self.__str__()
  def __eq__(self, other):
    return self.term == other.term

class EventQueue:
  '''
  ASAP realizes this API and gives it to the EventProvider for providing events
  (implementation in derived class)
  '''
  def append(self, event):
    '''
    add event to end of queue
    '''
    debug('enqueued event '+str(event))
  def immediate(self, event):
    '''
    add (immediate) event to beginning of queue
    '''
    debug('enqueued immediate '+str(event))

  def pop(self):
    '''get/pop an item from front'''
    pass

  def __iter__(self):
    '''
    provide iterator over queue contents
    '''
    return iter([])

class EventAPI:
  '''
  plugins realizing this API can add events to the event queue
  '''
  def __init__(self):
    self.queue = None
  def setQueue(self, queue):
    '''
    tell the EventAPI which EventQueue should be used
    '''
    assert(self.queue is None)
    self.queue = queue

class Environment:
  '''
  base class for environments
  an environment represents the view of the external world by the program
  applications will need to define its own environment
  TODO or could plugins define the environment and we automatically mix them together?
  '''
  def __str__(self):
    return 'Environment()'

class Input:
  '''
  base class for providing input to actions and externals
  '''
  def __init__(self, environment, inputs, interpretation=None):
    """
    environment: derived from api.Environment
    inputs: tuple of api.Term
    interpretation: set of api.Term
    """
    self.environment = environment
    self.inputs = inputs
    self.interpretation = interpretation
  def __str__(self):
    interpretationinfo = 'empty'
    if self.interpretation is not None:
      interpretationinfo = 'contains {} terms'.format(len(self.interpretation))
    return "Input(environment={},inputs={},interpretation {})".format(
      self.environment, self.inputs, interpretationinfo)
  def __repr__(self):
    return self.__str__()

class ExternalInput(Input):
  '''
  provides all data that an external receives for its computation
  '''
  def __init__(self, environment, inputs, interpretation=None):
    Input.__init__(self, environment, inputs, interpretation)

class External:
  '''
  a handler for an external
  '''
  @property
  def interface(self):
    '''
    return interface of the external as a tuple
    (name,in_arity,in_arity_mandatory,out_arity)
    e.g. Xt.temperature[sensorname](reading) would have interface
      ('temperature',1,1,1)
    e.g. Xt.concat[str1,str2,...](out) would have interface
      ('concat',99,2,1)
    '''
    pass
  def query(self, einput):
    '''
    evaluate the external relative to the ExternalInput einput
    return an iterable of tuples of output terms (api.Term objects) for this external
    (if the arity is 1, the output shall be an iterable over tuples of size one)
    '''
    return []

class ExternalAPI:
  '''
  plugins realizing this API can provide externals
  '''
  def externals(self):
    '''
    provide iterable of External objects
    '''
    return []

class ActionInput(Input):
  '''
  provides all data that an action receives for its execution
  '''
  def __init__(self, environment, inputs, interpretation=None):
    Input.__init__(self, environment, inputs, interpretation)

class Action:
  '''
  a handler for an action
  '''
  @property
  def interface(self):
    '''
    return interface of the action as a tuple
    (name,in_arity,in_arity_mandatory)
    e.g. Do.drawString(align,pos,string[,color]) would have interface
      ('drawString',4,3)
    '''
    pass
  def execute(self, ainput):
    '''
    execute the action relative to the ActionInput ainput
    '''
    pass

class DoAPI:
  '''
  plugins realizing this API can provide actions
  '''
  def actions(self):
    '''
    provide iterable of Action objects
    '''
    return []
  def beforeExecution(self):
    '''
    this method is called before executing actions from an answer set (even if no actions are executed)
    '''
    pass
  def afterExecution(self):
    '''
    this method is called after executing actions from an answer set (even if no actions are executed)
    '''
    pass

class Backend:
  '''
  a backend/engine realizes this interface
  '''
  def evaluate(self, program, plugins=[], environment=None, fluentfile=None):
    '''
    evaluate given ASAP program
    program is the program to evaluate 
    plugins is an iterable of objects of type
      DoAPI, ExternalAPI, EventAPI, or combinations thereof
    environment is the initial environment
    fluentfile is the file to load fluents from (json format)
    '''
    pass

# TODO provide base class for plugin?
# TODO provide method for registering plugins
