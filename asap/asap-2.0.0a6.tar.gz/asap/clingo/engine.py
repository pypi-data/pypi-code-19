import sys
import os
import argparse
import importlib
import logging
import traceback

import clingo

from .. import core
from .common import *

ASAP_PATH = os.path.join(
  os.path.dirname(os.path.realpath(__file__)),
  '../')
CORE_PATH = os.path.join(ASAP_PATH,'./core/')

class EventCallable:
  def __init__(self, currentEvent):
    self.event = termToClingoSym(currentEvent.term)
    if __debug__:
      logging.debug("@event() = {}".format(repr(self.event)))
  def __call__(self):
    ret = [self.event]
    #debug("@event() = {}".format(repr(ret)))
    return ret

class PrevvalCallable:
  def __init__(self, fluents):
    self.fluents = fluents
    self.ret = [ (termToClingoSym(kv[0]), termToClingoSym(kv[1])) for kv in self.fluents.items() ]
    if __debug__:
      logging.debug("@prevval() = {}".format(repr(self.ret)))
  def __call__(self):
    #debug("@prevval() = {}".format(repr(ret)))
    return self.ret

class ExternalCallable:
  def __init__(self, external, environment, exceptions):
    self.external = external
    self.name, self.in_arity, self.in_arity_mand, self.out_arity = external.interface
    self.environment = environment
    self.exceptions = exceptions
  def __call__(self, *arguments):
    #debug("external {} called with {}".format(self.name, repr(arguments)))
    try:
      nargs = len(arguments)
      if nargs < self.in_arity_mand or nargs > self.in_arity:
        raise Exception("invalid number of arguments for external {}: got {}, expected between {} and {}".format(
          self.name, repr(arguments), self.in_arity_mand, self.in_arity))
      apiArguments = [ clingoSymToTerm(a) for a in arguments ]
      queryinput = api.ExternalInput(self.environment, apiArguments)
      #debug("calling external {} with {}".format(self.name, repr(apiArguments)))
      out_tuples = self.external.query(queryinput)
      #if __debug__:
      #  logging.debug("external {}{} returned {}".format(self.name, repr(apiArguments), repr(out_tuples)))
      ret = []
      for ot in out_tuples:
        if len(ot) != self.out_arity:
          logging.warning("external {} returned output {} which is not of expected arity {} (ignoring)".format(self.name, repr(ot), self.out_arity))
        if not all([isinstance(t, api.Term) for t in ot]):
          raise Exception("external {} returned {} which are not api.Term instances".format(self.name, repr(list(ot))))
        otclingo = [termToClingoSym(x) for x in ot]
        # clingo expects a fun or a tuple of more than one thing
        if len(otclingo) == 1:
          clingotuple = otclingo[0]
        else:
          clingotuple = tuple(otclingo)
        #debug("@{}({}) = {}".format(self.name, repr(arguments), repr(clingotuple)))
        ret.append(clingotuple)
      if __debug__:
        logging.debug("gringo external {}{} returns {}".format(self.name, repr(arguments), repr(ret)))
      if len(ret) == 0 and self.out_arity == 1:
        # add dummy tuple, otherwise Gringo ignores (at least in 5.2.0)
        # TODO bug report to potassco
        ret.append( clingo.Function('dummy') )
      return ret
    except Exception as e:
      logging.warning(traceback.format_exc())
      self.exceptions.append("exception in external {}: {}".format(self.name, traceback.format_exc()))

class GroundingContext:
  '''
  this is used as 'context' for calling Control.ground
  it provides external grounding functions of form @func(arg1, ...)
  '''
  def __init__(self, externals, environment, fluents, currentEvent):
    self.exceptions = []
    self.externals = externals
    self.environment = environment
    self.fluents = fluents
    self.currentEvent = currentEvent
    self.callables = dict()
    self.callables['event'] = EventCallable(self.currentEvent)
    self.callables['prevval'] = PrevvalCallable(self.fluents)
    for name, e in externals.items():
      self.callables[name] = ExternalCallable(e, self.environment, self.exceptions)

  def __getattr__(self, name):
    '''
    called if a non-existing attribute (method, member variable) is used
    '''
    if name in self.callables:
      return self.callables[name]
    # an exception raised here is printed but otherwise ignored by clingo code
    # we collect exceptions and raise them from outside
    self.exceptions.append("GroundingContext.__getattr__ for '{}' (did you forget to load an external plugin?)".format(name))

    # return Fun(str(int(delay_ms)))
    #return Fun('"' + str(a).strip('"') + str(b).strip('"') + '"')
    #return Fun('"' + str(a).strip('"') + str(b).strip('"') + str(c).strip('"') + str(d).strip('"') + '"')

class ClingoBackend(api.Backend):
  '''
  the clingo realization of ASAP
  '''
  def __init__(self):
    self.exit = None # exit code, or None if no exit requested
    self.eq = core.EventQueueImpl()
  def evaluate(self, program, plugins_=[], environment=None, fluentfile=None):
    # prepare queue
    self.eq.append(api.Event(api.Term('initial_event')))
    doApis, eventApis, externalApis = core.separateApis(plugins_)
    core.registerQueue(eventApis, self.eq)
    # get dictionaries of actions and externals
    actions, externals = core.actionsFromApis(doApis), core.externalsFromApis(externalApis)

    rewritten = core.rewrite(program, target='clasp')
    fluents = core.FluentStorage()

    def utf8fromfile(path):
      with open(path, 'r', encoding='utf8') as f:
        return f.read()
    auxcode = utf8fromfile(os.path.join(CORE_PATH, 'fluents-common.lp')) + \
      utf8fromfile(os.path.join(CORE_PATH, 'fluents-clasp.lp'))

    logging.debug("starting main loop")
    iteration = 1
    while self.exit is None:
      currentEvent = self.eq.pop()
      ctx = GroundingContext(externals, environment, fluents, currentEvent)

      clingoargs = ['2']
      if logging.getLogger().isEnabledFor(logging.DEBUG):
        # output ground program
        clingoargs.append('--verbose')
        clingoargs.append('--output-debug=all')
      else:
        clingoargs.append('--warn=no-atom-undefined')
      parts = [ ('base', []) ]

      ctrl = clingo.Control(clingoargs)
      ctrl.add('base', [], rewritten + auxcode)
      try:
        ctrl.ground(parts, ctx)
      except:
        logging.critical("ctrl.ground exception "+traceback.format_exc())
      if len(ctx.exceptions) > 0:
        raise Exception('grounding exception: '+', '.join(ctx.exceptions))
      
      answersets = []
      def onModel(mdl):
        if __debug__:
          logging.debug('onModel got '+str(mdl))
        answersets.append(set([ clingoSymToTerm(a) for a in mdl.symbols(atoms=True) ]))
      ret = ctrl.solve(on_model=onModel)

      if len(answersets) == 0:
        raise Exception("no answer sets!")
      elif len(answersets) != 1:
        raise Exception("more than one answer set!")
      answerset = answersets[0]
      if __debug__:
        logging.debug("processing answer set {}".format(answerset))

      fluents = core.extractFluents(answerset)
      if __debug__:
        logging.debug("new fluent values: {}".format(fluents.nice()))

      actionSchedule = core.extractActions(answerset)
      core.executeActionSchedule(doApis, actions, environment, answerset, actionSchedule)
      logging.debug("iteration %d finished",iteration)
      iteration += 1

class ExitPlugin(api.DoAPI):
  '''plugin providing exit() action'''

  class ExitAction(api.Action):
    def __init__(self, clingo_backend):
      self.clingo_backend = clingo_backend
    @property
    def interface(self):
      return ('exit', 1, 1)
    def execute(self, ainput):
      assert(isinstance(ainput, api.ActionInput))
      assert(len(ainput.inputs) in [1, 1])
      if __debug__:
        logging.debug('ExitAction.execute({})'.format(repr(ainput)))
      try:
        # try to interpret exit code
        code = int(ainput.inputs[0].pred)
      except:
        traceback.format_exc()
        code = -1
      self.clingo_backend.exit = code

  def __init__(self, clingo_backend):
    self.clingo_backend = clingo_backend
  def actions(self):
    return [self.ExitAction(self.clingo_backend)]

class ImmediatePlugin(api.DoAPI):
  '''plugin providing immediate(<info>) action'''

  class ImmediateAction(api.Action):
    def __init__(self, clingo_backend):
      self.clingo_backend = clingo_backend
    @property
    def interface(self):
      return ('immediate', 1, 1)
    def execute(self, ainput):
      assert(isinstance(ainput, api.ActionInput))
      assert(len(ainput.inputs) in [1, 1])
      self.clingo_backend.eq.immediate(api.Event(api.Term('immediate', [ainput.inputs[0]])))

  def __init__(self, clingo_backend):
    self.clingo_backend = clingo_backend
  def actions(self):
    return [self.ImmediateAction(self.clingo_backend)]

loadedPlugins = {}
def loadPlugins(pluginnames):
  loaded_plugins_in_order = []
  for pn in pluginnames:
    pmodule = None
    try:
      pmodule = importlib.import_module(pn)
    except:
      raise Exception("loading plugin module '{}' failed: {}".format(pn, traceback.format_exc()))
    else:
      try:
        p = pmodule.Plugin()
        loadedPlugins[pn] = p
        loaded_plugins_in_order.append(p)
      except:
        raise Exception("instantiating plugin '{}' failed: {}".format(pn, traceback.format_exc()))
  return loaded_plugins_in_order

