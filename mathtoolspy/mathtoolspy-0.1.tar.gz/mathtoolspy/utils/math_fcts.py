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

"""
The MathFct contains some mathematically method, which are not supported by the Python lib.
"""

from mathconst import DOUBLE_TOL


def abs_sign(a, b):
    ''' The absolute value of A with the sign of B.'''
    return abs(a) if b >= 0 else -abs(a)


def sign(x):
    '''
    Returns the sign of the double number x.
    -1 if x < 0. 1 if x > 0 and 0 if x == 0
    '''
    if x < 0:
        return -1
    elif x > 0:
        return 1
    else:
        return 0


def float_equal(x, y, tol=DOUBLE_TOL):
    return abs(x - y) < tol


def interpolation_linear(x, x1, x2, y1, y2):
    """
    Linear interpolation
    returns (y2 - y1) / (x2 - x1) * (x - x1) + y1
    """
    m = (y2 - y1) / (x2 - x1)
    t = (x - x1)
    return m * t + y1


def interpolation_bilinear(x, y, x1, x2, y1, y2, z11, z21, z22, z12):
    '''
    The points (x_i, y_i) and values z_ij are connected as follows:
    Starting from lower left going in mathematically positive direction, i.e. counter clockwise.
    Therefore: (x1,y1,z11), (x2,y1,z21), (x2,y2,z22), (x1,y2,z12).
    '''
    t = (x - x1) / (x2 - x1)
    s = (y - y1) / (y2 - y1)
    v1 = (1.0 - t) * (1.0 - s) * z11
    v2 = t * (1.0 - s) * z21
    v3 = t * s * z22
    v4 = (1.0 - t) * s * z12
    ret = v1 + v2 + v3 + v4
    return ret


class FctWithCount(object):
    def __init__(self, fct):
        self.fct = fct
        self.number_of_calls = 0

    def __call__(self, x):
        self.number_of_calls += 1
        return self.fct(x)


class CompositionFct:
    def __init__(self, *fcts):
        self.fcts = fcts[::-1]

    def __call__(self, x):
        ret = x
        for fct in self.fcts:
            ret = fct(ret)
        return ret
