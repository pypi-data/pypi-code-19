from __future__ import division

inf = float("inf")

from ._bracket import bracket
from ._brent import brent

_eps = 1.4902e-08

def minimize(f, x0=None, x1=None, a=-inf, b=+inf, gfactor=2,
             rtol=_eps, atol=_eps, maxiter=500):
    r"""Function minimization.

    Applies :func:`brent_search.bracket` and then :func:`brent_search.brent`
    to find the minimum.

    Args:
        f (callable): function of interest.
        x0 (:obj:`float`, optional): first point.
        x1 (:obj:`float`, optional): second point.
        a (:obj:`float`, optional): interval's lower limit. Defaults to ``-inf``.
        b (:obj:`float`, optional): interval's upper limit. Defaults to ``+inf``.
        gfactor (:obj:`float`, optional): growing factor.
        rtol (:obj:`float`, optional): relative tolerance. Defaults to ``1.4902e-08``.
        atol (:obj:`float`, optional): absolute tolerance. Defaults to ``1.4902e-08``.
        maxiter (:obj:`int`, optional): maximum number of iterations. Defaults to ``500``.

    Returns:
        A tuple containing the found solution (if any) in the first position,
        the function evaluated at that point, and the number of function
        evaluations.
    """

    def func(x):
        func.nfev += 1
        return f(x)
    func.nfev = 0


    r, _ = bracket(func, x0=x0, x1=x1, a=a, b=b, gfactor=gfactor, rtol=rtol,
                       atol=atol, maxiter=maxiter)

    x0, x1, x2, f0, f1, f2 = r[0], r[1], r[2], r[3], r[4], r[5]
    x0, f0 = brent(func, x0, x2, f0, f2, x1, f1, rtol, atol, maxiter)[0:2]
    return x0, f0, func.nfev
