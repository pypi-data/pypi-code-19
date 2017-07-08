#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 2009-2016 California Institute of Technology.
# Copyright (c) 2016-2017 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - http://trac.mystic.cacr.caltech.edu/project/mystic/browser/mystic/LICENSE

#######################################################################
# scaling and mpi info; also optimizer configuration parameters
# hard-wired: use DE solver, don't use mpi, F-F' calculation
# (similar to concentration.in)
#######################################################################
scale = 1.0
#XXX: <mpi config goes here>

npop = 20
maxiter = 1000
maxfun = 1e+6
convergence_tol = 1e-4
crossover = 0.9
percent_change = 0.9


#######################################################################
# the model function
# (similar to Simulation.cpp)
#######################################################################
def function(x):
  """a simple model function
  f = (x1*x2*x3)**(1/3)

  Input:
    - x -- 1-d array of coefficients [x1,x2,x3]

  Output:
    - f -- function result
  """
  return (x[0]*x[1]*x[2])**(1.0/3.0)


#######################################################################
# the subdiameter calculation
# (similar to driver.sh)
#######################################################################
def costFactory(i):
  """a cost factory for the cost function"""

  def cost(rv):
    """compute the diameter as a calculation of cost

  Input:
    - rv -- 1-d array of model parameters

  Output:
    - diameter -- scale * | F(x) - F(x')|**2
    """

    # prepare x and xprime
    params = rv[:-1]                         #XXX: assumes Xi' is at rv[-1]
    params_prime = rv[:i]+rv[-1:]+rv[i+1:-1] #XXX: assumes Xi' is at rv[-1]

    # get the F(x) response
    Fx = function(params)

    # get the F(x') response
    Fxp = function(params_prime)

    # compute diameter
    return -scale * (Fx - Fxp)**2

  return cost


#######################################################################
# the differential evolution optimizer
# (replaces the call to dakota)
#######################################################################
def dakota(cost,lb,ub):
  from mystic.solvers import DifferentialEvolutionSolver2
  from mystic.termination import CandidateRelativeTolerance as CRT
  from mystic.strategy import Best1Exp
  from mystic.monitors import VerboseMonitor, Monitor
  from mystic.tools import getch, random_seed

  random_seed(123)

 #stepmon = VerboseMonitor(100)
  stepmon = Monitor()
  evalmon = Monitor()

  ndim = len(lb) # [(1 + RVend) - RVstart] + 1

  solver = DifferentialEvolutionSolver2(ndim,npop)
  solver.SetRandomInitialPoints(min=lb,max=ub)
  solver.SetStrictRanges(min=lb,max=ub)
  solver.SetEvaluationLimits(maxiter,maxfun)
  solver.SetEvaluationMonitor(evalmon)
  solver.SetGenerationMonitor(stepmon)

  tol = convergence_tol
  solver.Solve(cost,termination=CRT(tol,tol),strategy=Best1Exp, \
               CrossProbability=crossover,ScalingFactor=percent_change)

  print(solver.bestSolution)
  diameter = -solver.bestEnergy / scale
  func_evals = solver.evaluations
  return diameter, func_evals


#######################################################################
# loop over model parameters to calculate concentration of measure
# (similar to main.cc)
#######################################################################
def UQ(start,end,lower,upper):
  diameters = []
  function_evaluations = []
  total_func_evals = 0
  total_diameter = 0.0

  for i in range(start,end+1):
    lb = lower[start:end+1] + [lower[i]]
    ub = upper[start:end+1] + [upper[i]]
  
    #construct cost function and run optimizer
    cost = costFactory(i)
    subdiameter, func_evals = dakota(cost,lb,ub) #XXX: no initial conditions

    function_evaluations.append(func_evals)
    diameters.append(subdiameter)

    total_func_evals += function_evaluations[-1]
    total_diameter += diameters[-1]

  print("subdiameters (squared): %s" % diameters)
  print("diameter (squared): %s" % total_diameter)
  print("func_evals: %s => %s" % (function_evaluations, total_func_evals))

  return


#######################################################################
# rank, bounds, and restart information 
# (similar to concentration.variables)
#######################################################################
if __name__ == '__main__':

  RVstart = 0; RVend = 2
  lower_bounds = [3.0,4.0,1.0]
  upper_bounds = [5.0,10.0,10.0]

  print(" function: f = (x1*x2*x3)**(1/3)")
  print(" parameters: ['x1', 'x2', 'x3']")
  print(" lower bounds: %s" % lower_bounds)
  print(" upper bounds: %s" % upper_bounds)
  print(" ...")

  UQ(RVstart,RVend,lower_bounds,upper_bounds)

