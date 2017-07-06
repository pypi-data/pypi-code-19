"""Functions for generating interesting polynomials, e.g. for benchmarking. """

from __future__ import print_function, division

from sympy.core import Add, Mul, Symbol, sympify, Dummy, symbols
from sympy.functions.elementary.miscellaneous import sqrt
from sympy.core.singleton import S

from sympy.polys.polytools import Poly, PurePoly
from sympy.polys.polyutils import _analyze_gens

from sympy.polys.polyclasses import DMP

from sympy.polys.densebasic import (
    dmp_zero, dmp_one, dmp_ground,
    dup_from_raw_dict, dmp_raise, dup_random
)

from sympy.polys.densearith import (
    dmp_add_term, dmp_neg, dmp_mul, dmp_sqr
)

from sympy.polys.factortools import (
    dup_zz_cyclotomic_poly
)

from sympy.polys.domains import ZZ

from sympy.ntheory import nextprime

from sympy.utilities import subsets, public

from sympy.core.compatibility import range


@public
def swinnerton_dyer_poly(n, x=None, **args):
    """Generates n-th Swinnerton-Dyer polynomial in `x`.  """
    from .numberfields import minimal_polynomial
    if n <= 0:
        raise ValueError(
            "can't generate Swinnerton-Dyer polynomial of order %s" % n)

    if x is not None:
        sympify(x)
    else:
        x = Dummy('x')

    if n > 3:
        p = 2
        a = [sqrt(2)]
        for i in range(2, n + 1):
            p = nextprime(p)
            a.append(sqrt(p))
        return minimal_polynomial(Add(*a), x, polys=args.get('polys', False))

    if n == 1:
        ex = x**2 - 2
    elif n == 2:
        ex = x**4 - 10*x**2 + 1
    elif n == 3:
        ex = x**8 - 40*x**6 + 352*x**4 - 960*x**2 + 576
    if not args.get('polys', False):
        return ex
    else:
        return PurePoly(ex, x)

@public
def cyclotomic_poly(n, x=None, **args):
    """Generates cyclotomic polynomial of order `n` in `x`. """
    if n <= 0:
        raise ValueError(
            "can't generate cyclotomic polynomial of order %s" % n)

    poly = DMP(dup_zz_cyclotomic_poly(int(n), ZZ), ZZ)

    if x is not None:
        poly = Poly.new(poly, x)
    else:
        poly = PurePoly.new(poly, Dummy('x'))

    if not args.get('polys', False):
        return poly.as_expr()
    else:
        return poly


@public
def symmetric_poly(n, *gens, **args):
    """Generates symmetric polynomial of order `n`. """
    gens = _analyze_gens(gens)

    if n < 0 or n > len(gens) or not gens:
        raise ValueError("can't generate symmetric polynomial of order %s for %s" % (n, gens))
    elif not n:
        poly = S.One
    else:
        poly = Add(*[ Mul(*s) for s in subsets(gens, int(n)) ])

    if not args.get('polys', False):
        return poly
    else:
        return Poly(poly, *gens)


@public
def random_poly(x, n, inf, sup, domain=ZZ, polys=False):
    """Return a polynomial of degree ``n`` with coefficients in ``[inf, sup]``. """
    poly = Poly(dup_random(n, inf, sup, domain), x, domain=domain)

    if not polys:
        return poly.as_expr()
    else:
        return poly


@public
def interpolating_poly(n, x, X='x', Y='y'):
    """Construct Lagrange interpolating polynomial for ``n`` data points. """
    if isinstance(X, str):
        X = symbols("%s:%s" % (X, n))

    if isinstance(Y, str):
        Y = symbols("%s:%s" % (Y, n))

    coeffs = []

    for i in range(0, n):
        numer = []
        denom = []

        for j in range(0, n):
            if i == j:
                continue

            numer.append(x - X[j])
            denom.append(X[i] - X[j])

        numer = Mul(*numer)
        denom = Mul(*denom)

        coeffs.append(numer/denom)

    return Add(*[ coeff*y for coeff, y in zip(coeffs, Y) ])


def fateman_poly_F_1(n):
    """Fateman's GCD benchmark: trivial GCD """
    Y = [ Symbol('y_' + str(i)) for i in range(0, n + 1) ]

    y_0, y_1 = Y[0], Y[1]

    u = y_0 + Add(*[ y for y in Y[1:] ])
    v = y_0**2 + Add(*[ y**2 for y in Y[1:] ])

    F = ((u + 1)*(u + 2)).as_poly(*Y)
    G = ((v + 1)*(-3*y_1*y_0**2 + y_1**2 - 1)).as_poly(*Y)

    H = Poly(1, *Y)

    return F, G, H


def dmp_fateman_poly_F_1(n, K):
    """Fateman's GCD benchmark: trivial GCD """
    u = [K(1), K(0)]

    for i in range(0, n):
        u = [dmp_one(i, K), u]

    v = [K(1), K(0), K(0)]

    for i in range(0, n):
        v = [dmp_one(i, K), dmp_zero(i), v]

    m = n - 1

    U = dmp_add_term(u, dmp_ground(K(1), m), 0, n, K)
    V = dmp_add_term(u, dmp_ground(K(2), m), 0, n, K)

    f = [[-K(3), K(0)], [], [K(1), K(0), -K(1)]]

    W = dmp_add_term(v, dmp_ground(K(1), m), 0, n, K)
    Y = dmp_raise(f, m, 1, K)

    F = dmp_mul(U, V, n, K)
    G = dmp_mul(W, Y, n, K)

    H = dmp_one(n, K)

    return F, G, H


def fateman_poly_F_2(n):
    """Fateman's GCD benchmark: linearly dense quartic inputs """
    Y = [ Symbol('y_' + str(i)) for i in range(0, n + 1) ]

    y_0 = Y[0]

    u = Add(*[ y for y in Y[1:] ])

    H = Poly((y_0 + u + 1)**2, *Y)

    F = Poly((y_0 - u - 2)**2, *Y)
    G = Poly((y_0 + u + 2)**2, *Y)

    return H*F, H*G, H


def dmp_fateman_poly_F_2(n, K):
    """Fateman's GCD benchmark: linearly dense quartic inputs """
    u = [K(1), K(0)]

    for i in range(0, n - 1):
        u = [dmp_one(i, K), u]

    m = n - 1

    v = dmp_add_term(u, dmp_ground(K(2), m - 1), 0, n, K)

    f = dmp_sqr([dmp_one(m, K), dmp_neg(v, m, K)], n, K)
    g = dmp_sqr([dmp_one(m, K), v], n, K)

    v = dmp_add_term(u, dmp_one(m - 1, K), 0, n, K)

    h = dmp_sqr([dmp_one(m, K), v], n, K)

    return dmp_mul(f, h, n, K), dmp_mul(g, h, n, K), h


def fateman_poly_F_3(n):
    """Fateman's GCD benchmark: sparse inputs (deg f ~ vars f) """
    Y = [ Symbol('y_' + str(i)) for i in range(0, n + 1) ]

    y_0 = Y[0]

    u = Add(*[ y**(n + 1) for y in Y[1:] ])

    H = Poly((y_0**(n + 1) + u + 1)**2, *Y)

    F = Poly((y_0**(n + 1) - u - 2)**2, *Y)
    G = Poly((y_0**(n + 1) + u + 2)**2, *Y)

    return H*F, H*G, H


def dmp_fateman_poly_F_3(n, K):
    """Fateman's GCD benchmark: sparse inputs (deg f ~ vars f) """
    u = dup_from_raw_dict({n + 1: K.one}, K)

    for i in range(0, n - 1):
        u = dmp_add_term([u], dmp_one(i, K), n + 1, i + 1, K)

    v = dmp_add_term(u, dmp_ground(K(2), n - 2), 0, n, K)

    f = dmp_sqr(
        dmp_add_term([dmp_neg(v, n - 1, K)], dmp_one(n - 1, K), n + 1, n, K), n, K)
    g = dmp_sqr(dmp_add_term([v], dmp_one(n - 1, K), n + 1, n, K), n, K)

    v = dmp_add_term(u, dmp_one(n - 2, K), 0, n - 1, K)

    h = dmp_sqr(dmp_add_term([v], dmp_one(n - 1, K), n + 1, n, K), n, K)

    return dmp_mul(f, h, n, K), dmp_mul(g, h, n, K), h

# A few useful polynomials from Wang's paper ('78).

from sympy.polys.rings import ring

def _f_0():
    R, x, y, z = ring("x,y,z", ZZ)
    return x**2*y*z**2 + 2*x**2*y*z + 3*x**2*y + 2*x**2 + 3*x + 4*y**2*z**2 + 5*y**2*z + 6*y**2 + y*z**2 + 2*y*z + y + 1

def _f_1():
    R, x, y, z = ring("x,y,z", ZZ)
    return x**3*y*z + x**2*y**2*z**2 + x**2*y**2 + 20*x**2*y*z + 30*x**2*y + x**2*z**2 + 10*x**2*z + x*y**3*z + 30*x*y**2*z + 20*x*y**2 + x*y*z**3 + 10*x*y*z**2 + x*y*z + 610*x*y + 20*x*z**2 + 230*x*z + 300*x + y**2*z**2 + 10*y**2*z + 30*y*z**2 + 320*y*z + 200*y + 600*z + 6000

def _f_2():
    R, x, y, z = ring("x,y,z", ZZ)
    return x**5*y**3 + x**5*y**2*z + x**5*y*z**2 + x**5*z**3 + x**3*y**2 + x**3*y*z + 90*x**3*y + 90*x**3*z + x**2*y**2*z - 11*x**2*y**2 + x**2*z**3 - 11*x**2*z**2 + y*z - 11*y + 90*z - 990

def _f_3():
    R, x, y, z = ring("x,y,z", ZZ)
    return x**5*y**2 + x**4*z**4 + x**4 + x**3*y**3*z + x**3*z + x**2*y**4 + x**2*y**3*z**3 + x**2*y*z**5 + x**2*y*z + x*y**2*z**4 + x*y**2 + x*y*z**7 + x*y*z**3 + x*y*z**2 + y**2*z + y*z**4

def _f_4():
    R, x, y, z = ring("x,y,z", ZZ)
    return -x**9*y**8*z - x**8*y**5*z**3 - x**7*y**12*z**2 - 5*x**7*y**8 - x**6*y**9*z**4 + x**6*y**7*z**3 + 3*x**6*y**7*z - 5*x**6*y**5*z**2 - x**6*y**4*z**3 + x**5*y**4*z**5 + 3*x**5*y**4*z**3 - x**5*y*z**5 + x**4*y**11*z**4 + 3*x**4*y**11*z**2 - x**4*y**8*z**4 + 5*x**4*y**7*z**2 + 15*x**4*y**7 - 5*x**4*y**4*z**2 + x**3*y**8*z**6 + 3*x**3*y**8*z**4 - x**3*y**5*z**6 + 5*x**3*y**4*z**4 + 15*x**3*y**4*z**2 + x**3*y**3*z**5 + 3*x**3*y**3*z**3 - 5*x**3*y*z**4 + x**2*z**7 + 3*x**2*z**5 + x*y**7*z**6 + 3*x*y**7*z**4 + 5*x*y**3*z**4 + 15*x*y**3*z**2 + y**4*z**8 + 3*y**4*z**6 + 5*z**6 + 15*z**4

def _f_5():
    R, x, y, z = ring("x,y,z", ZZ)
    return -x**3 - 3*x**2*y + 3*x**2*z - 3*x*y**2 + 6*x*y*z - 3*x*z**2 - y**3 + 3*y**2*z - 3*y*z**2 + z**3

def _f_6():
    R, x, y, z, t = ring("x,y,z,t", ZZ)
    return 2115*x**4*y + 45*x**3*z**3*t**2 - 45*x**3*t**2 - 423*x*y**4 - 47*x*y**3 + 141*x*y*z**3 + 94*x*y*z*t - 9*y**3*z**3*t**2 + 9*y**3*t**2 - y**2*z**3*t**2 + y**2*t**2 + 3*z**6*t**2 + 2*z**4*t**3 - 3*z**3*t**2 - 2*z*t**3

def _w_1():
    R, x, y, z = ring("x,y,z", ZZ)
    return 4*x**6*y**4*z**2 + 4*x**6*y**3*z**3 - 4*x**6*y**2*z**4 - 4*x**6*y*z**5 + x**5*y**4*z**3 + 12*x**5*y**3*z - x**5*y**2*z**5 + 12*x**5*y**2*z**2 - 12*x**5*y*z**3 - 12*x**5*z**4 + 8*x**4*y**4 + 6*x**4*y**3*z**2 + 8*x**4*y**3*z - 4*x**4*y**2*z**4 + 4*x**4*y**2*z**3 - 8*x**4*y**2*z**2 - 4*x**4*y*z**5 - 2*x**4*y*z**4 - 8*x**4*y*z**3 + 2*x**3*y**4*z + x**3*y**3*z**3 - x**3*y**2*z**5 - 2*x**3*y**2*z**3 + 9*x**3*y**2*z - 12*x**3*y*z**3 + 12*x**3*y*z**2 - 12*x**3*z**4 + 3*x**3*z**3 + 6*x**2*y**3 - 6*x**2*y**2*z**2 + 8*x**2*y**2*z - 2*x**2*y*z**4 - 8*x**2*y*z**3 + 2*x**2*y*z**2 + 2*x*y**3*z - 2*x*y**2*z**3 - 3*x*y*z + 3*x*z**3 - 2*y**2 + 2*y*z**2

def _w_2():
    R, x, y = ring("x,y", ZZ)
    return 24*x**8*y**3 + 48*x**8*y**2 + 24*x**7*y**5 - 72*x**7*y**2 + 25*x**6*y**4 + 2*x**6*y**3 + 4*x**6*y + 8*x**6 + x**5*y**6 + x**5*y**3 - 12*x**5 + x**4*y**5 - x**4*y**4 - 2*x**4*y**3 + 292*x**4*y**2 - x**3*y**6 + 3*x**3*y**3 - x**2*y**5 + 12*x**2*y**3 + 48*x**2 - 12*y**3

def f_polys():
    return _f_0(), _f_1(), _f_2(), _f_3(), _f_4(), _f_5(), _f_6()

def w_polys():
    return _w_1(), _w_2()
