# -*- coding: utf-8 -*-

#  mathtoolspy
#  ------------
#  A fast, efficient Python library for mathematically operations, like
#  integration, solver, distributions and other useful functions.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/businessdate
#  License: APACHE Version 2 License (see LICENSE file)


from mathtoolspy.solver import minimize_algorithm_1dim_brent


class MinimizeAlgorithmNDimPowell(object):
    '''
    The minimazation with the Powell algorithm.
    Press, et al., 'Numerical Recipes in C', 2nd ed, Powell (p.412).

    Minimization of a function func of n variables. Input consists of an initial starting
    point p[0..n-1]; an inital matrix xi[0..n-1,0..n-1], whose columns contain the initial
    set of directions (usually the n unit vectors); and ftol, the fractional tolerance in
    the function value such that failure to decrease by more than this amount on one
    iteration signals doneness. On output, p is set to best point found, xi is the
    then-current direction set, fret is the returned function value at p. The routine linmin is used.
    ***
    Initial matrix xi[0..n-1,0..n-1], whose columns contain the initial
    set of directions (usually the n unit vectors). On output xi is the then-current
    direction set.
    ***
    Initial starting point p[0..n-1]. On output p is set to best point found.
    '''

    TINY = 1.0e-25
    TOL = 2.0e-4

    def __init__(self):
        self.brent = minimize_algorithm_1dim_brent

    def FindMinimun(self, fct, initial_point, tol):
        ndim = initial_point.count()
        # On output Powell sets the initial point to best point found.
        tpoint = initial_point
        # Choose the unit vectors as initial set of directions.
        directions = self._initialize_directions(ndim)
        # Locate the minimum and store the number of iterations.
        r = self.powell(directions, tpoint, ndim, tol, fct)

        return r

    def _initialize_directions(self, ndim):
        ret = ((0 if i != j else 1 for i in range(ndim)) for j in range(ndim))
        return ret

    def powell(self, initial_xvalues, initial_fvalues, ndim, tol, fct):
        p = initial_fvalues
        xi = initial_xvalues
