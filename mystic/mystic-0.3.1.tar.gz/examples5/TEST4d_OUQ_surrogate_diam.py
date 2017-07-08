#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2010-2016 California Institute of Technology.
# Copyright (c) 2016-2017 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - http://trac.mystic.cacr.caltech.edu/project/mystic/browser/mystic/LICENSE

debug = False
MINMAX = -1  ## NOTE: sup = maximize = -1; inf = minimize = 1
#######################################################################
# scaling and mpi info; also optimizer configuration parameters
# hard-wired: use DE solver, don't use mpi, F-F' calculation
#######################################################################
npop = 40
maxiter = 1000
maxfun = 1e+6
convergence_tol = 1e-6; ngen = 40
crossover = 0.9
percent_change = 0.9


#######################################################################
# the model function
#######################################################################
from surrogate import marc_surr as model


#######################################################################
# the differential evolution optimizer
#######################################################################
def optimize(cost,_bounds,_constraints):
  from mystic.solvers import DifferentialEvolutionSolver2
  from mystic.termination import ChangeOverGeneration as COG
  from mystic.strategy import Best1Exp
  from mystic.monitors import VerboseMonitor, Monitor
  from mystic.tools import random_seed

 #random_seed(123)

  stepmon = VerboseMonitor(2)
 #stepmon = Monitor()
  evalmon = Monitor()

  lb,ub = _bounds
  ndim = len(lb)

  solver = DifferentialEvolutionSolver2(ndim,npop)
  solver.SetRandomInitialPoints(min=lb,max=ub)
  solver.SetStrictRanges(min=lb,max=ub)
  solver.SetEvaluationLimits(maxiter,maxfun)
  solver.SetEvaluationMonitor(evalmon)
  solver.SetGenerationMonitor(stepmon)
  solver.SetConstraints(_constraints)

  tol = convergence_tol
  solver.Solve(cost,termination=COG(tol,ngen),strategy=Best1Exp, \
               CrossProbability=crossover,ScalingFactor=percent_change)

  solved = solver.bestSolution
 #print("solved: %s" % solver.Solution())
  func_max = MINMAX * solver.bestEnergy       #NOTE: -solution assumes -Max
 #func_max = 1.0 + MINMAX*solver.bestEnergy   #NOTE: 1-sol => 1-success = fail
  func_evals = solver.evaluations
  from mystic.munge import write_support_file
  write_support_file(stepmon, npts=npts)
  return solved, func_max, func_evals


#######################################################################
# maximize the function
#######################################################################
def maximize(params,npts,bounds):

  from mystic.math.measures import split_param
  from mystic.math.discrete import product_measure
  from mystic.math import almostEqual
  from numpy import inf
  atol = 1e-18 # default is 1e-18
  rtol = 1e-7  # default is 1e-7
  target,error = params
  lb,ub = bounds

  # split lower & upper bounds into weight-only & sample-only
  w_lb, x_lb = split_param(lb, npts)
  w_ub, x_ub = split_param(ub, npts)

  # NOTE: rv, lb, ub are of the form:
  #    rv = [wxi]*nx + [xi]*nx + [wyi]*ny + [yi]*ny + [wzi]*nz + [zi]*nz

  # generate secondary constraints function
  def more_constraints(c): #XXX: move within 'def constraints'?
    ##################### begin function-specific #####################
#   E = float(c[0].var)  # var(h)
#   if not (E <= float(target[1] + error[1])) \
#   or not (float(target[1] - error[1]) <= E):
#     c[0].var = target[1]

    E = float(c[0].mean)  # mean(h)
    if not (E <= float(target[2] + error[2])) \
    or not (float(target[2] - error[2]) <= E):
      c[0].mean = target[2]

    E = float(c[2].mean)  # mean(v)
    if not (E <= float(target[3] + error[3])) \
    or not (float(target[3] - error[3]) <= E):
      c[2].mean = target[3]
    ###################### end function-specific ######################
    return c

  # generate primary constraints function
  def constraints(rv):
    c = product_measure()
    c.load(rv, npts)
    # NOTE: bounds wi in [0,1] enforced by filtering
    # impose norm on each discrete measure
    for measure in c:
      if not almostEqual(float(measure.mass), 1.0, tol=atol, rel=rtol):
        measure.normalize()
    # impose expectation on product measure
    ##################### begin function-specific #####################
    E = float(c.expect(model))
    if not (E <= float(target[0] + error[0])) \
    or not (float(target[0] - error[0]) <= E):
      c.set_expect((target[0],error[0]), model, (x_lb,x_ub), more_constraints)

    # c = more_constraints(c) #XXX: impose constraints again (necessary ?)
    ###################### end function-specific ######################
    # extract weights and positions
    return c.flatten()

  # generate maximizing function
  def cost(rv):
    c = product_measure()
    c.load(rv, npts)
    #XXX: apply 'filters' to catch errors in constraints solver (necessary ?)
    ##################### begin function-specific #####################
    E = float(c.expect(model))
    if E > (target[0] + error[0]) or E < (target[0] - error[0]):
      if debug: print("skipping expect: %s" % E)
      return inf  #XXX: FORCE TO SATISFY E CONSTRAINTS

#   E = float(c[0].var)  # var(h)
#   if E > (target[1] + error[1]) or E < (target[1] - error[1]):
#     if debug: print("skipping variance: %s" % E)
#     return inf  #XXX: FORCE TO SATISFY E CONSTRAINTS

    E = float(c[0].mean)  # mean(h)
    if E > (target[2] + error[2]) or E < (target[2] - error[2]):
      if debug: print("skipping expect: %s" % E)
      return inf  #XXX: FORCE TO SATISFY E CONSTRAINTS

    E = float(c[2].mean)  # mean(v)
    if E > (target[3] + error[3]) or E < (target[3] - error[3]):
      if debug: print("skipping expect: %s" % E)
      return inf  #XXX: FORCE TO SATISFY E CONSTRAINTS
    ###################### end function-specific ######################
    return MINMAX * c.pof(model)

  # maximize
  solved, func_max, func_evals = optimize(cost,(lb,ub),constraints)

  if MINMAX == 1:
    print("func_minimum: %s" % func_max)  # inf
  else:
    print("func_maximum: %s" % func_max)  # sup
  print("func_evals: %s" % func_evals)

  return solved, func_max


#######################################################################
# rank, bounds, and restart information 
#######################################################################
if __name__ == '__main__':
  function_name = model.__name__

  H_mean = 6.5    #NOTE: SET THE 'mean' HERE!
  H_range = 1.0   #NOTE: SET THE 'range' HERE!
# h_var = 168.75  #NOTE: SET THE 'mean' HERE!
# h_vrange = 5.0  #NOTE: SET THE 'range' HERE!
  h_var = None    #NOTE: SET THE 'mean' HERE!
  h_vrange = None #NOTE: SET THE 'range' HERE!
  h_mean = 82.5   #NOTE: SET THE 'mean' HERE!
  h_range = 0.5   #NOTE: SET THE 'range' HERE!
  v_mean = 2.45   #NOTE: SET THE 'mean' HERE!
  v_range = 0.05  #NOTE: SET THE 'range' HERE!
  target = (H_mean,h_var,h_mean,v_mean)      #XXX: 4D-expect
  error = (H_range,h_vrange,h_range,v_range) #XXX: 4D-expect
  nx = 2  #NOTE: SET THE NUMBER OF 'h' POINTS HERE!
  ny = 2  #NOTE: SET THE NUMBER OF 'a' POINTS HERE!
  nz = 2  #NOTE: SET THE NUMBER OF 'v' POINTS HERE!

  w_lower = [0.0]
  w_upper = [1.0]
  h_lower = [60.0];  a_lower = [0.0];  v_lower = [2.1]
  h_upper = [105.0]; a_upper = [30.0]; v_upper = [2.8]

  lower_bounds = (nx * w_lower) + (nx * h_lower) \
               + (ny * w_lower) + (ny * a_lower) \
               + (nz * w_lower) + (nz * v_lower) 
  upper_bounds = (nx * w_upper) + (nx * h_upper) \
               + (ny * w_upper) + (ny * a_upper) \
               + (nz * w_upper) + (nz * v_upper) 

  print("...SETTINGS...")
  print("npop = %s" % npop)
  print("maxiter = %s" % maxiter)
  print("maxfun = %s" % maxfun)
  print("convergence_tol = %s" % convergence_tol)
  print("crossover = %s" % crossover)
  print("percent_change = %s" % percent_change)
  print("..............\n")

  print(" model: f(x) = %s(x)" % function_name)
  print(" target: %s" % str(target))
  print(" error: %s" % str(error))
  print(" npts: %s" % str((nx,ny,nz)))
  print("..............\n")

  param_string = "["
  for i in range(nx):
    param_string += "'wx%s', " % str(i+1)
  for i in range(nx):
    param_string += "'x%s', " % str(i+1)
  for i in range(ny):
    param_string += "'wy%s', " % str(i+1)
  for i in range(ny):
    param_string += "'y%s', " % str(i+1)
  for i in range(nz):
    param_string += "'wz%s', " % str(i+1)
  for i in range(nz):
    param_string += "'z%s', " % str(i+1)
  param_string = param_string[:-2] + "]"

  print(" parameters: %s" % param_string)
  print(" lower bounds: %s" % lower_bounds)
  print(" upper bounds: %s" % upper_bounds)
# print(" ...")
  pars = (target,error)
  npts = (nx,ny,nz)
  bounds = (lower_bounds,upper_bounds)
  solved, diameter = maximize(pars,npts,bounds)

  from numpy import array
  from mystic.math.discrete import product_measure
  c = product_measure()
  c.load(solved,npts)
  print("solved: [wx,x]\n%s" % array(list(zip(c[0].weights,c[0].positions))))
  print("solved: [wy,y]\n%s" % array(list(zip(c[1].weights,c[1].positions))))
  print("solved: [wz,z]\n%s" % array(list(zip(c[2].weights,c[2].positions))))
 
  # XXX: 4D-expect
  print("expect: %s" % str( c.expect(model) ))
  print("var (x): %s" % str( c[0].var ))   # var(h)
  print("mean(x): %s" % str( c[0].mean ))  # mean(h)
  print("mean(z): %s" % str( c[2].mean ))  # mean(v)

# EOF
