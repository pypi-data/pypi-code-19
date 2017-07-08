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


from mathtoolspy.utils.mathconst import GOLD as C
from mathtoolspy.utils.mathconst import DOUBLE_TOL, ONE_MINUS_GOLD as R


def minimize_algorithm_1dim_golden(function, a, b, c, tolerance=DOUBLE_TOL):
    '''
    Given a function f, and given a bracketing triplet of abscissas ax, bx, cx
    (such that bx is between ax and cx, and f(bx) is less than both f(ax) and f(cx)),
    this routine performs a golden section search for the minimum, isolating it to
    a fractional precision of about tol. The abscissa of the minimum is returned as xmin,
    and the minimum function value is returned as Golden, the returned function value.
    See Press, et al. (1992) "Numerical recipes in C", 2nd ed., p.401.
    '''

    x0 = a
    x3 = c
    if abs(c - b) > abs(b - a):
        x1 = b
        x2 = b + c * (c - b)
    else:
        x2 = b
        x1 = b - c * (b - a)
    f1 = function(x1)
    f2 = function(x2)
    counter = 0
    while abs(x3 - x0) - tolerance * (abs(x1) + abs(x2)) > DOUBLE_TOL:
        """print("------")
        print("x0 = " + str(x0))
        print("x1 = " + str(x1))
        print("x2 = " + str(x2))
        print("x3 = " + str(x3))
        print("f1 = " + str(f1))
        print("f2 = " + str(f2))
        print("tolerance * (abs(x1) + abs(x2) = " + str(tolerance * (abs(x1) + abs(x2))))
        print("abs(x3 - x0) = " + str(abs(x3 - x0)))"""

        if f2 < f1:
            x0 = x1
            x1 = x2
            x2 = R * x1 + C * x3
            f1 = f2
            f2 = function(x2)
        else:
            x3 = x2
            x2 = x1
            x1 = R * x2 + C * x0
            f2 = f1
            f1 = function(x1)
        counter = counter + 1
        if counter > 10000:
            raise Exception("More than 10000 iterations.")
    if f1 < f2:
        return (x1, f1)
    else:
        return (x2, f2)
