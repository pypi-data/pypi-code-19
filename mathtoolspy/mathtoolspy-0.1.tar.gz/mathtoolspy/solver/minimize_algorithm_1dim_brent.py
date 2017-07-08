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


from mathtoolspy.utils.mathconst import DOUBLE_TOL, GOLD

from mathtoolspy.utils.math_fcts import float_equal, abs_sign


def shift(a, b, c):
    ''' The shift function returns the values as tuple.'''
    return a, b, c


# devFct, tInitialValue, tolerance, Optimizer.MAX_NUMBER_OF_FUNCTION_CALLS
def minimize_algorithm_1dim_brent(fct, _a, _b, _c, tolerance=DOUBLE_TOL):
    '''
    Finds the minimum of the given function f. The arguments are the given function f, and given a bracketing triplet of abscissas A, B, C
    (such that B is between A and C, and f(B) is less than both f(A) and f(C)) and the Tolerance.
    This routine isolates the minimum to a fractional precision of about tol using
    Brent's method. The abscissa of of the minimum is returned as xmin, and the minimum
    value is returned as brent, the returned function value.
    '''

    ''' ZEPS is a small number that protects against trying to achieve fractional accuracy
    for a minimum that happens to be exactly zero. '''
    ZEPS = 1.0e-10

    a = _a if _a < _c else _c
    b = _a if _a > _c else _c
    assert a < _b and _b < b

    x = w = v = _b;
    fv = fw = fx = fct(x)
    tol1 = tolerance
    d = e = 0.0
    e_temp = fu = u = xm = 0.0
    iterations = 0

    while (True):
        xm = 0.5 * (a + b)
        tol1 = tolerance * abs(x) + ZEPS
        tol2 = 2.0 * tol1;
        if abs(x - xm) <= tol2 - 0.5 * (b - a):
            return (x, fx)
        if abs(e) > tol1:
            r = (x - w) * (fx - fv)
            q = (x - v) * (fx - fw)
            p = (x - v) * q - (x - w) * r
            q = 2.0 * (q - r)
            if q > 0.0:
                p = -p
            q = abs(q)
            e_temp = e
            e = d
            if abs(p) >= abs(0.5 * q * e_temp) or p <= q * (a - x) or p >= q * (b - x):
                e = a - x if x >= xm else b - x
                d = GOLD * e
            else:
                d = p / q
                u = x + d
                if u - a < tol2 or b - u < tol2:
                    d = abs_sign(tol1, xm - x)
        else:
            e = a - x if x >= xm else b - x
            d = GOLD * e

        u = x + d if abs(d) >= tol1 else x + abs_sign(tol1, d)
        fu = fct(u);
        if fu <= fx:
            if u >= x:
                a = x
            else:
                b = x
            v, w, x = shift(w, x, u)
            fv, fw, fx = shift(fw, fx, fu)
        else:
            if u < x:
                a = u
            else:
                b = u
        if fu <= fw or float_equal(w, x):
            v = w
            w = u
            fv = fw
            fw = fu
        elif float_equal(fu, fv) or float_equal(v, x) or float_equal(v, w):
            v = u
            fv = fu

        iterations = iterations + 1
        if iterations > 10000:
            return (None, None)
