from sympy import Rational, sqrt, symbols, sin, exp, log, sinh, cosh, cos, pi, \
    I, erf, tan, asin, asinh, acos, Function, Derivative, diff, simplify, \
    LambertW, Eq, Piecewise, Symbol, Add, ratsimp, Integral, Sum, \
    besselj, besselk, bessely, jn
from sympy.integrals.heurisch import components, heurisch, heurisch_wrapper
from sympy.utilities.pytest import XFAIL, skip, slow, ON_TRAVIS
from sympy.integrals.integrals import integrate
x, y, z, nu = symbols('x,y,z,nu')
f = Function('f')

def test_components():
    assert components(x*y, x) == {x}
    assert components(1/(x + y), x) == {x}
    assert components(sin(x), x) == {sin(x), x}
    assert components(sin(x)*sqrt(log(x)), x) == \
        {log(x), sin(x), sqrt(log(x)), x}
    assert components(x*sin(exp(x)*y), x) == \
        {sin(y*exp(x)), x, exp(x)}
    assert components(x**Rational(17, 54)/sqrt(sin(x)), x) == \
        {sin(x), x**Rational(1, 54), sqrt(sin(x)), x}

    assert components(f(x), x) == \
        {x, f(x)}
    assert components(Derivative(f(x), x), x) == \
        {x, f(x), Derivative(f(x), x)}
    assert components(f(x)*diff(f(x), x), x) == \
        {x, f(x), Derivative(f(x), x), Derivative(f(x), x)}

def test_issue_10680():
    assert isinstance(integrate(x**log(x**log(x**log(x))),x), Integral)

def test_heurisch_polynomials():
    assert heurisch(1, x) == x
    assert heurisch(x, x) == x**2/2
    assert heurisch(x**17, x) == x**18/18


def test_heurisch_fractions():
    assert heurisch(1/x, x) == log(x)
    assert heurisch(1/(2 + x), x) == log(x + 2)
    assert heurisch(1/(x + sin(y)), x) == log(x + sin(y))

    # Up to a constant, where C = 5*pi*I/12, Mathematica gives identical
    # result in the first case. The difference is because sympy changes
    # signs of expressions without any care.
    # XXX ^ ^ ^ is this still correct?
    assert heurisch(5*x**5/(
        2*x**6 - 5), x) in [5*log(2*x**6 - 5) / 12, 5*log(-2*x**6 + 5) / 12]
    assert heurisch(5*x**5/(2*x**6 + 5), x) == 5*log(2*x**6 + 5) / 12

    assert heurisch(1/x**2, x) == -1/x
    assert heurisch(-1/x**5, x) == 1/(4*x**4)


def test_heurisch_log():
    assert heurisch(log(x), x) == x*log(x) - x
    assert heurisch(log(3*x), x) == -x + x*log(3) + x*log(x)
    assert heurisch(log(x**2), x) in [x*log(x**2) - 2*x, 2*x*log(x) - 2*x]


def test_heurisch_exp():
    assert heurisch(exp(x), x) == exp(x)
    assert heurisch(exp(-x), x) == -exp(-x)
    assert heurisch(exp(17*x), x) == exp(17*x) / 17
    assert heurisch(x*exp(x), x) == x*exp(x) - exp(x)
    assert heurisch(x*exp(x**2), x) == exp(x**2) / 2

    assert heurisch(exp(-x**2), x) is None

    assert heurisch(2**x, x) == 2**x/log(2)
    assert heurisch(x*2**x, x) == x*2**x/log(2) - 2**x*log(2)**(-2)

    assert heurisch(Integral(x**z*y, (y, 1, 2), (z, 2, 3)).function, x) == (x*x**z*y)/(z+1)
    assert heurisch(Sum(x**z, (z, 1, 2)).function, z) == x**z/log(x)

def test_heurisch_trigonometric():
    assert heurisch(sin(x), x) == -cos(x)
    assert heurisch(pi*sin(x) + 1, x) == x - pi*cos(x)

    assert heurisch(cos(x), x) == sin(x)
    assert heurisch(tan(x), x) in [
        log(1 + tan(x)**2)/2,
        log(tan(x) + I) + I*x,
        log(tan(x) - I) - I*x,
    ]

    assert heurisch(sin(x)*sin(y), x) == -cos(x)*sin(y)
    assert heurisch(sin(x)*sin(y), y) == -cos(y)*sin(x)

    # gives sin(x) in answer when run via setup.py and cos(x) when run via py.test
    assert heurisch(sin(x)*cos(x), x) in [sin(x)**2 / 2, -cos(x)**2 / 2]
    assert heurisch(cos(x)/sin(x), x) == log(sin(x))

    assert heurisch(x*sin(7*x), x) == sin(7*x) / 49 - x*cos(7*x) / 7
    assert heurisch(1/pi/4 * x**2*cos(x), x) == 1/pi/4*(x**2*sin(x) -
                    2*sin(x) + 2*x*cos(x))

    assert heurisch(acos(x/4) * asin(x/4), x) == 2*x - (sqrt(16 - x**2))*asin(x/4) \
        + (sqrt(16 - x**2))*acos(x/4) + x*asin(x/4)*acos(x/4)


def test_heurisch_hyperbolic():
    assert heurisch(sinh(x), x) == cosh(x)
    assert heurisch(cosh(x), x) == sinh(x)

    assert heurisch(x*sinh(x), x) == x*cosh(x) - sinh(x)
    assert heurisch(x*cosh(x), x) == x*sinh(x) - cosh(x)

    assert heurisch(
        x*asinh(x/2), x) == x**2*asinh(x/2)/2 + asinh(x/2) - x*sqrt(4 + x**2)/4


def test_heurisch_mixed():
    assert heurisch(sin(x)*exp(x), x) == exp(x)*sin(x)/2 - exp(x)*cos(x)/2


def test_heurisch_radicals():
    assert heurisch(1/sqrt(x), x) == 2*sqrt(x)
    assert heurisch(1/sqrt(x)**3, x) == -2/sqrt(x)
    assert heurisch(sqrt(x)**3, x) == 2*sqrt(x)**5/5

    assert heurisch(sin(x)*sqrt(cos(x)), x) == -2*sqrt(cos(x))**3/3
    y = Symbol('y')
    assert heurisch(sin(y*sqrt(x)), x) == 2/y**2*sin(y*sqrt(x)) - \
        2*sqrt(x)*cos(y*sqrt(x))/y
    assert heurisch_wrapper(sin(y*sqrt(x)), x) == Piecewise(
        (0, Eq(y, 0)),
        (-2*sqrt(x)*cos(sqrt(x)*y)/y + 2*sin(sqrt(x)*y)/y**2, True))
    y = Symbol('y', positive=True)
    assert heurisch_wrapper(sin(y*sqrt(x)), x) == 2/y**2*sin(y*sqrt(x)) - \
        2*sqrt(x)*cos(y*sqrt(x))/y


def test_heurisch_special():
    assert heurisch(erf(x), x) == x*erf(x) + exp(-x**2)/sqrt(pi)
    assert heurisch(exp(-x**2)*erf(x), x) == sqrt(pi)*erf(x)**2 / 4


def test_heurisch_symbolic_coeffs():
    assert heurisch(1/(x + y), x) == log(x + y)
    assert heurisch(1/(x + sqrt(2)), x) == log(x + sqrt(2))
    assert simplify(diff(heurisch(log(x + y + z), y), y)) == log(x + y + z)


def test_heurisch_symbolic_coeffs_1130():
    y = Symbol('y')
    assert heurisch_wrapper(1/(x**2 + y), x) == Piecewise(
        (-1/x, Eq(y, 0)),
        (-I*log(x - I*sqrt(y))/(2*sqrt(y)) + I*log(x + I*sqrt(y))/(2*sqrt(y)), True))
    y = Symbol('y', positive=True)
    assert heurisch_wrapper(1/(x**2 + y), x) in [I/sqrt(y)*log(x + sqrt(-y))/2 -
    I/sqrt(y)*log(x - sqrt(-y))/2, I*log(x + I*sqrt(y)) /
        (2*sqrt(y)) - I*log(x - I*sqrt(y))/(2*sqrt(y))]


def test_heurisch_hacking():
    assert heurisch(sqrt(1 + 7*x**2), x, hints=[]) == \
        x*sqrt(1 + 7*x**2)/2 + sqrt(7)*asinh(sqrt(7)*x)/14
    assert heurisch(sqrt(1 - 7*x**2), x, hints=[]) == \
        x*sqrt(1 - 7*x**2)/2 + sqrt(7)*asin(sqrt(7)*x)/14

    assert heurisch(1/sqrt(1 + 7*x**2), x, hints=[]) == \
        sqrt(7)*asinh(sqrt(7)*x)/7
    assert heurisch(1/sqrt(1 - 7*x**2), x, hints=[]) == \
        sqrt(7)*asin(sqrt(7)*x)/7

    assert heurisch(exp(-7*x**2), x, hints=[]) == \
        sqrt(7*pi)*erf(sqrt(7)*x)/14

    assert heurisch(1/sqrt(9 - 4*x**2), x, hints=[]) == \
        asin(2*x/3)/2

    assert heurisch(1/sqrt(9 + 4*x**2), x, hints=[]) == \
        asinh(2*x/3)/2

def test_heurisch_function():
    assert heurisch(f(x), x) is None

@XFAIL
def test_heurisch_function_derivative():
    # TODO: it looks like this used to work just by coincindence and
    # thanks to sloppy implementation. Investigate why this used to
    # work at all and if support for this can be restored.

    df = diff(f(x), x)

    assert heurisch(f(x)*df, x) == f(x)**2/2
    assert heurisch(f(x)**2*df, x) == f(x)**3/3
    assert heurisch(df/f(x), x) == log(f(x))

def test_heurisch_wrapper():
    f = 1/(y + x)
    assert heurisch_wrapper(f, x) == log(x + y)
    f = 1/(y - x)
    assert heurisch_wrapper(f, x) == -log(x - y)
    f = 1/((y - x)*(y + x))
    assert heurisch_wrapper(f, x) == \
        Piecewise((1/x, Eq(y, 0)), (log(x + y)/2/y - log(x - y)/2/y, True))
    # issue 6926
    f = sqrt(x**2/((y - x)*(y + x)))
    assert heurisch_wrapper(f, x) == x*sqrt(x**2)*sqrt(1/(-x**2 + y**2)) \
        - y**2*sqrt(x**2)*sqrt(1/(-x**2 + y**2))/x

def test_issue_3609():
    assert heurisch(1/(x * (1 + log(x)**2)), x) == I*log(log(x) + I)/2 - \
        I*log(log(x) - I)/2

### These are examples from the Poor Man's Integrator
### http://www-sop.inria.fr/cafe/Manuel.Bronstein/pmint/examples/

def test_pmint_rat():
    # TODO: heurisch() is off by a constant: -3/4. Possibly different permutation
    # would give the optimal result?

    def drop_const(expr, x):
        if expr.is_Add:
            return Add(*[ arg for arg in expr.args if arg.has(x) ])
        else:
            return expr

    f = (x**7 - 24*x**4 - 4*x**2 + 8*x - 8)/(x**8 + 6*x**6 + 12*x**4 + 8*x**2)
    g = (4 + 8*x**2 + 6*x + 3*x**3)/(x**5 + 4*x**3 + 4*x) + log(x)

    assert drop_const(ratsimp(heurisch(f, x)), x) == g

def test_pmint_trig():
    f = (x - tan(x)) / tan(x)**2 + tan(x)
    g = -x**2/2 - x/tan(x) + log(tan(x)**2 + 1)/2

    assert heurisch(f, x) == g

@slow # 8 seconds on 3.4 GHz
def test_pmint_logexp():
    if ON_TRAVIS:
        # See https://github.com/sympy/sympy/pull/12795
        skip("Too slow for travis.")

    f = (1 + x + x*exp(x))*(x + log(x) + exp(x) - 1)/(x + log(x) + exp(x))**2/x
    g = log(x + exp(x) + log(x)) + 1/(x + exp(x) + log(x))

    assert ratsimp(heurisch(f, x)) == g

@slow # 8 seconds on 3.4 GHz
@XFAIL  # there's a hash dependent failure lurking here
def test_pmint_erf():
    f = exp(-x**2)*erf(x)/(erf(x)**3 - erf(x)**2 - erf(x) + 1)
    g = sqrt(pi)*log(erf(x) - 1)/8 - sqrt(pi)*log(erf(x) + 1)/8 - sqrt(pi)/(4*erf(x) - 4)

    assert ratsimp(heurisch(f, x)) == g

def test_pmint_LambertW():
    f = LambertW(x)
    g = x*LambertW(x) - x + x/LambertW(x)

    assert heurisch(f, x) == g

def test_pmint_besselj():
    f = besselj(nu + 1, x)/besselj(nu, x)
    g = nu*log(x) - log(besselj(nu, x))

    assert heurisch(f, x) == g

    f = (nu*besselj(nu, x) - x*besselj(nu + 1, x))/x
    g = besselj(nu, x)

    assert heurisch(f, x) == g

    f = jn(nu + 1, x)/jn(nu, x)
    g = nu*log(x) - log(jn(nu, x))

    assert heurisch(f, x) == g

@slow
def test_pmint_bessel_products():
    # Note: Derivatives of Bessel functions have many forms.
    # Recurrence relations are needed for comparisons.
    if ON_TRAVIS:
        skip("Too slow for travis.")

    f = x*besselj(nu, x)*bessely(nu, 2*x)
    g = -2*x*besselj(nu, x)*bessely(nu - 1, 2*x)/3 + x*besselj(nu - 1, x)*bessely(nu, 2*x)/3

    assert heurisch(f, x) == g

    f = x*besselj(nu, x)*besselk(nu, 2*x)
    g = -2*x*besselj(nu, x)*besselk(nu - 1, 2*x)/5 - x*besselj(nu - 1, x)*besselk(nu, 2*x)/5

    assert heurisch(f, x) == g

@slow # 110 seconds on 3.4 GHz
def test_pmint_WrightOmega():
    if ON_TRAVIS:
        skip("Too slow for travis.")
    def omega(x):
        return LambertW(exp(x))

    f = (1 + omega(x) * (2 + cos(omega(x)) * (x + omega(x))))/(1 + omega(x))/(x + omega(x))
    g = log(x + LambertW(exp(x))) + sin(LambertW(exp(x)))

    assert heurisch(f, x) == g

def test_RR():
    # Make sure the algorithm does the right thing if the ring is RR. See
    # issue 8685.
    assert heurisch(sqrt(1 + 0.25*x**2), x, hints=[]) == \
        0.5*x*sqrt(0.25*x**2 + 1) + 1.0*asinh(0.5*x)

# TODO: convert the rest of PMINT tests:
# Airy functions
# f = (x - AiryAi(x)*AiryAi(1, x)) / (x**2 - AiryAi(x)**2)
# g = Rational(1,2)*ln(x + AiryAi(x)) + Rational(1,2)*ln(x - AiryAi(x))
# f = x**2 * AiryAi(x)
# g = -AiryAi(x) + AiryAi(1, x)*x
# Whittaker functions
# f = WhittakerW(mu + 1, nu, x) / (WhittakerW(mu, nu, x) * x)
# g = x/2 - mu*ln(x) - ln(WhittakerW(mu, nu, x))
