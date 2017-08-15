from asap.core import api

import sys
import threading
import logging
import traceback

# we again use clingo here (independently from the main ASAP instance)
import clingo
import asap.clingo.common as clingo_common

class SolverStartAction(api.Action):
  '''
  Do.start_solver(<name>,<pred>) 2 mandatory arguments
  <name> is string
  <pred> is a binary predicate:
  * <pred>(file,<file>) adds content of <file> to the program to be evaluated
  * <pred>(rule,<rule>) adds <rule> to the program to be evaluated
  * <pred>(limit,<int>) uses <int> as a limit for the answer sets to be enumerated
  '''
  def __init__(self, plugin):
    self.plugin = plugin

  @property
  def interface(self):
    return ('solver_start', 2, 2)

  def execute(self, ainput):
    assert(len(ainput.inputs) == 2)
    name, pred = ainput.inputs
    name, pred = str(name), str(pred)
    # extract info using predicate
    #logging.debug("ainput.interpretation is "+repr(ainput.interpretation))
    # default: enumerate all answer sets
    program, limit = [], 0
    for atom in [ a for a in ainput.interpretation if a.pred == pred ]:
      #logging.debug("processing relevant predicate input "+repr(atom))
      type_, arg = str(atom.args[0]), atom.args[1]
      if type_ == 'file':
        fname = arg.unquoted()
        #logging.debug("solver '%s' loading from file '%s'", name, fname)
        with open(fname,'r') as f:
          program.append(f.read())
      elif type_ == 'rule':
        rule = arg.unquoted()
        #logging.debug("solver '%s' adding rule '%s'", name, rule)
        program.append(rule)
      elif type_ == 'limit':
        limit = int(arg)
    if name in self.plugin.solver:
      #logging.debug("deleting solver "+repr(name))
      del(self.plugin.solver[name])
    # TODO assemble program
    newsolver = Solver(name, self.plugin.queue, '\n'.join(program), limit)
    self.plugin.solver[name] = newsolver
    newsolver.start()

class SolverStartedExternal(api.External):
  '''
  output: solver handles that have been started
  '''
  def __init__(self, plugin):
    self.plugin = plugin
  @property
  def interface(self):
    # name, in_arity, in_arity_mandatory, out_arity
    return ('solver_started',0,0,1)
  def query(self, einput):
    assert(len(einput.inputs) == 0)
    return [ (api.Term(n_s[0]),)
             for n_s in self.plugin.solver.items()
             if n_s[1].is_started() ]

class SolverFinishedExternal(api.External):
  '''
  output: solver handles that have finished solving
  (if there is no result, no answer set handles will be available!)
  '''
  def __init__(self, plugin):
    self.plugin = plugin
  @property
  def interface(self):
    # name, in_arity, in_arity_mandatory, out_arity
    return ('solver_finished',0,0,1)
  def query(self, einput):
    assert(len(einput.inputs) == 0)
    return [ (api.Term(n_s[0]),)
             for n_s in self.plugin.solver.items()
             if n_s[1].is_finished() ]

class AnswersetsExternal(api.External):
  '''
  return handle to answer sets of solver (if solver has finished enumerating)
  input: solver handle (given to Do.solver_start)
  output: one handle for each answer set (integer)
  '''
  def __init__(self, plugin):
    self.plugin = plugin
  @property
  def interface(self):
    # name, in_arity, in_arity_mandatory, out_arity
    return ('solver_answersets',1,1,1)
  def query(self, einput):
    assert(len(einput.inputs) == 1)
    handle = str(einput.inputs[0])
    if handle in self.plugin.solver:
      solver = self.plugin.solver[handle]
      if solver.is_finished():
        return [ (api.Term(i),) for i in range(0,len(solver.get_answersets())) ]
    return []

class ExtensionExternal(api.External):
  '''
  return extension of given handle/answerset/predicate
  (if solver has finished enumerating)
  input: solver handle (str, given to Do.solver_start)
  input: answer set handle (int)
  input: predicate (str)
  output: composite term c(...) containing tuple of extension
  '''
  def __init__(self, plugin):
    self.plugin = plugin
  @property
  def interface(self):
    # name, in_arity, in_arity_mandatory, out_arity
    return ('solver_extension',3,3,1)
  def query(self, einput):
    assert(len(einput.inputs) == 3)
    sname, ahandle, pred = einput.inputs
    try:
      sname, ahandle, pred = str(sname), int(ahandle), str(pred)
    except:
      if str(ahandle) == "dummy":
        return [] # see engine-clingo.py to understand where "dummy" comes from
      logging.warning("got wrong input type for solver_extension {} {} {}: {}".format(
        repr(sname), repr(ahandle), repr(pred), traceback.format_exc()))
      return []
    if sname in self.plugin.solver:
      solver = self.plugin.solver[sname]
      if solver.is_finished() and ahandle in range(0, len(solver.get_answersets())):
        answerset = solver.get_answersets()[ahandle]
        return [ (api.Term('c', t.args),) for t in answerset if t.pred == pred ]
    return []

class Solver:
  def __init__(self, name, eventqueue, program, answersetlimit=1):
    self.name = name
    self.queue = eventqueue
    self.program = program
    self.answersetlimit = answersetlimit
    self.thread = None
    self.answersets = None
  def start(self):
    assert(self.thread is None)
    self.thread = threading.Thread(target=self.run)
    self.thread.daemon = True
    self.thread.start()
  def run(self):
    # main entry point, started when solver is started
    logging.debug("solver '%s' starting: sending program", self.name)
    clingoargs = []
    #clingoargs.append('--output-debug=all')
    clingoargs.append(self.answersetlimit)
    try:
      ctrl = clingo.Control(clingoargs)
      if __debug__:
        for r in self.program.split('\n'):
          logging.debug("solver '%s' program %s", self.name, r.strip('\n'))
      ctrl.add('base', [], self.program)
      parts = [ ('base',[]) ] 
      ctrl.ground(parts)
    except:
      logging.critical("solver '%s' grounding exception %s", self.name, traceback.format_exc())
      if __debug__:
        logging.critical("aborting from solver to facilitate debugging")
        sys.exit(-1)
    logging.debug("solver '%s' grounding finished: solving", self.name)
    answersets = set()
    def onModel(mdl):
      logging.debug("solver '%s' got model %s", self.name, str(mdl))
      answersets.add(frozenset([ clingo_common.clingoSymToTerm(a) for a in mdl.symbols(atoms=True) ]))
    ret = ctrl.solve(on_model=onModel)
    #logging.debug("solver '%s' got %d answer sets", self.name, len(answersets))
    # it was a set of answer sets, but make it a list so that we can index it
    self.answersets = list(answersets)
    # TODO cleanup program (and ctrl?)
    # notify the framework with an event that this solver has finished
    self.queue.append(api.Event(api.Term('solver_done',[api.Term(self.name),])))
  def is_started(self):
    return self.thread is not None
  def is_running(self):
    return self.thread is not None and self.answersets is None
  def is_finished(self):
    return self.thread is not None and self.answersets is not None
  def get_answersets(self):
    """
    returns a list of answer sets (frozenset of api.Term)
    """
    return self.answersets

class Plugin(api.DoAPI, api.EventAPI, api.ExternalAPI):
  def __init__(self):
    api.EventAPI.__init__(self)
    # started solver instances
    # key = handle
    # value = Solver instance
    self.solver = {}

  def actions(self):
    return [SolverStartAction(self)]

  def externals(self):
    return [AnswersetsExternal(self), ExtensionExternal(self), SolverStartedExternal(self), SolverFinishedExternal(self)]

