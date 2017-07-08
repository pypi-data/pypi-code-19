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


from math import cos

from mathtoolspy.utils.mathconst import PI


class GaussLegendreIntegrator():
    '''
    Gauss Legendre integrator, which uses the Gauss Legendre quadratures
    '''

    def __init__(self, steps=100):
        xgrid_and_weights = GaussLegendreQuadratures.get_values(steps)
        self._xgrid = xgrid_and_weights[0]
        self._weights = xgrid_and_weights[1]

    def integrate(self, function, lower_bound, upper_bound):
        if upper_bound < lower_bound:
            return -self.integrate(function, upper_bound, lower_bound)

        mid_point = 0.5 * (upper_bound - lower_bound)
        mean_point = 0.5 * (upper_bound + lower_bound)
        integral = 0
        for i in range(0, len(self._xgrid)):
            x = self._xgrid[i] + mean_point
            f = function(x)
            integral += self._weights[i] * f
        ret = mid_point * integral
        return ret

    def __call__(self, fct, lower_bound, upper_bound):
        return self.integrate(fct, lower_bound, upper_bound)


class GaussLegendreQuadratures:
    _xgrid_and_weights = {}

    @staticmethod
    def get_values(nsteps):
        ret = GaussLegendreQuadratures._xgrid_and_weights.get(nsteps)
        if ret != None:
            return ret

        ret = GaussLegendreQuadratures._gauss_legendre(nsteps)
        GaussLegendreQuadratures._xgrid_and_weights[nsteps] = ret
        return ret

    @staticmethod
    def _gauss_legendre(nsteps):
        n = nsteps
        xgrid = n * [0]
        weights = n * [0]
        m = (n + 1) // 2
        for i in range(1, m + 1):
            lengendreDerivative = GaussLegendreQuadratures._calc_legengre_polynom_derivativ(i, n)
            z = lengendreDerivative[0]
            pp = lengendreDerivative[1]
            xgrid[i - 1] = -z
            xgrid[n - i] = z
            w = 2 / ((1 - z * z) * pp * pp)
            weights[i - 1] = w
            weights[n - i] = w
        return [xgrid, weights]

    @staticmethod
    def _calc_legengre_polynom_derivativ(i, n):
        EPS = 3.0E-11
        z = cos(PI * (i - 0.25) / (n + 0.5))
        # z = MathFct.cos_real(MathConsts.PI * (i - 0.25) / (n + 0.5))
        pp = 0
        # Starting with the above approximation to the i-th root,
        # we enter the main loop of refinement by Newton's method.
        condition = True
        while condition:
            p1 = 1
            p2 = 0
            for j in range(1, n + 1):
                p3 = p2
                p2 = p1
                p1 = ((2 * j - 1) * z * p2 - (j - 1) * p3) / j
            # p1 is now the desired Legengre polynomial.
            # We next compute pp, its derivative
            # by a standard relation involving also p2,
            # the polynomial of one lower order.
            pp = n * (z * p1 - p2) / (z * z - 1)
            z1 = z
            z = z1 - p1 / pp
            condition = abs(z - z1) > EPS
        return [z, pp]
