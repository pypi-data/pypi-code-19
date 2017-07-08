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


class GaussLobattoStep:
    def __init__(self, function, alpha, beta, Is, max_number_of_iterations):
        self._function = function
        self._alpha = alpha
        self._beta = beta
        self._is = Is
        self._max_number_of_iterations = max_number_of_iterations
        self._used_iter = 0

    def adaptive_step(self, a, b, fa, fb):
        h = (b - a) / 2.0
        m = (a + b) / 2.0
        mll = m - self._alpha * h
        ml = m - self._beta * h
        mr = m + self._beta * h
        mrr = m + self._alpha * h
        fmll = self._function(mll)
        fml = self._function(ml)
        fm = self._function(m)
        fmr = self._function(mr)
        fmrr = self._function(mrr)

        i2 = (h / 6.0) * (fa + fb + 5.0 * (fml + fmr))
        i1 = (h / 1470.0) * (77.0 * (fa + fb) + 432.0 * (fmll + fmrr) + 625.0 * (fml + fmr) + 672.0 * fm)

        if self._is + (i1 - i2) == self._is or mll <= a or b <= mrr:
            if m <= a or b <= m:
                raise Exception("Interval contains no more machine number.")
            return i1

        self._used_iter += 1
        if self._used_iter > self._max_number_of_iterations:
            raise Exception("Maximal number of iterations " + str(self._max_number_of_iterations) + "'exceeded.")

        ret1 = self.adaptive_step(a, mll, fa, fmll)
        ret2 = self.adaptive_step(mll, ml, fmll, fml)
        ret3 = self.adaptive_step(ml, m, fml, fm)
        ret4 = self.adaptive_step(m, mr, fm, fmr)
        ret5 = self.adaptive_step(mr, mrr, fmr, fmrr)
        ret6 = self.adaptive_step(mrr, b, fmrr, fb)

        return ret1 + ret2 + ret3 + ret4 + ret5 + ret6


class GaussLobattoIntegrator:
    def __init__(self, max_number_of_iterations=255, abs_tolerance=1.0e-10):
        self.max_number_of_iterations = max_number_of_iterations
        self.abs_tolerance = abs_tolerance

    def integrate(self, function, lower_bound, upper_bound):
        if lower_bound == upper_bound:
            return 0
        if lower_bound > upper_bound:
            return -self.integrate(function, upper_bound, lower_bound)

        # three constants for the Gauss-Lobatto approach
        x1 = 0.942882415695480
        x2 = 0.641853342345781
        x3 = 0.236383199662150
        alpha = 0.816496580927726  # sqrt(2.0/3.0)
        beta = 0.447213595499958  # 1.0 / sqrt(5.0)
        m = (lower_bound + upper_bound) / 2.0
        h = (upper_bound - lower_bound) / 2.0

        fa = function(lower_bound)
        fb = function(upper_bound)

        f2 = function(m - x1 * h)
        f3 = function(m - alpha * h)
        f4 = function(m - x2 * h)
        f5 = function(m - beta * h)
        f6 = function(m - x3 * h)
        f7 = function(m)
        f8 = function(m + x3 * h)
        f9 = function(m + beta * h)
        f10 = function(m + x2 * h)
        f11 = function(m + alpha * h)
        f12 = function(m + x1 * h)

        w1 = 0.158271919734802
        w2 = 0.0942738402188500
        w3 = 0.155071987336585
        w4 = 0.188821573960182
        w5 = 0.199773405226859
        w6 = 0.224926465333340
        w7 = 0.242611071901408

        i2 = (h / 6.0) * (fa + fb + 5.0 * (f5 + f9))
        i1 = (h / 1470.0) * (77.0 * (fa + fb) + 432.0 * (f3 + f11) + 625.0 * (f5 + f9) + 672.0 * f7)
        Is = h * (w1 * (fa + fb)) + w2 * (f2 + f12) + w3 * (f3 + f11) + w4 * (f4 + f10) + w5 * (f5 + f9) + w6 * (
        f6 + f8) + w7 * f7
        sign = 1 if Is >= 0 else -1
        R = abs(i1 - Is) / abs(i2 - Is)

        tol = self.abs_tolerance
        tol = tol / R if R > 0 and R < 1 else tol
        Is = sign * abs(Is) * tol / 1E-12
        Is = upper_bound - lower_bound if Is == 0 else Is

        gls = GaussLobattoStep(function, alpha, beta, Is, self.max_number_of_iterations)
        ret = gls.adaptive_step(lower_bound, upper_bound, fa, fb)

        return ret

    def __call__(self, fct, lower_bound, upper_bound):
        return self.integrate(fct, lower_bound, upper_bound)
