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


from math import acos, sqrt, cos

from mathtoolspy.utils.mathconst import PI

from mathtoolspy.utils.math_fcts import sign


def roots_of_cubic_polynom(a1, a2, a3):
    '''
    Finds the roots of a 3 dim polymon of the form x^3 + a1 * x^2 + a2 * x + a3.
    The roots are returned as complex numbers.
    '''
    q = (a1 * a1 - 3.0 * a2) / 9.0
    r = (2 * a1 * a1 * a1 - 9.0 * a1 * a2 + 27.0 * a3) / 54.0
    r2 = r * r
    q3 = q * q * q
    a1d3 = a1 / 3.0

    if r2 - q3 >= 0.0:  # In this case there are 2 complex roots
        # Let a = - sgn(R) * ( |R| + sqrt(R^2 -Q^3) )^(1/3)
        oneThird = 1.0 / 3.0
        a = - sign(r) * (abs(r) + sqrt(r2 - q3)) ** oneThird
        b = q / a if a != 0.0 else 0.0
        apb = a + b
        root1 = complex(apb - a1d3)
        root2 = -0.5 * apb - a1d3 + sqrt(3) / 2.0 * (a1 - a2) * 1j
        root3 = root2.conjugate()
        return root1, root2, root3
    else:  # In this case there are three real roots
        theta = acos(r / sqrt(q3))
        fac = -2.0 * sqrt(q)
        root1 = complex(fac * cos(theta / 3.0) - a1d3)
        root2 = complex(fac * cos((theta + 2.0 * PI) / 3.0) - a1d3)
        root3 = complex(fac * cos((theta - 2.0 * PI) / 3.0) - a1d3)
        return root1, root2, root3
