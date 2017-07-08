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


class SimplexIntegrator:
    def logNone(self, x):
        pass

    def __init__(self, steps=100, log_info=None):
        self.nsteps = steps
        if log_info == None:
            self.log_info = self.logNone
        else:
            self.log_info = log_info

    def integrate(self, function, lower_bound, upper_bound):
        """
        Calculates the integral of the given one dimensional function
        in the interval from lower_bound to upper_bound, with the simplex integration method.
        """
        ret = 0.0
        n = self.nsteps
        xStep = (float(upper_bound) - float(lower_bound)) / float(n)
        self.log_info("xStep" + str(xStep))
        x = lower_bound
        val1 = function(x)
        self.log_info("val1: " + str(val1))
        for i in range(n):
            x = (i + 1) * xStep + lower_bound
            self.log_info("x: " + str(x))
            val2 = function(x)
            self.log_info("val2: " + str(val2))
            ret += 0.5 * xStep * (val1 + val2)
            val1 = val2
        return ret

    def __call__(self, function, lower_bound, upper_bound):
        return self.integrate(function, lower_bound, upper_bound)
