from sympy import symbols, Derivative, Integral, exp, cos, oo, Function
from sympy.functions.special.bessel import besselj
from sympy.functions.special.polynomials import legendre
from sympy.functions.combinatorial.numbers import bell
from sympy.printing.conventions import split_super_sub, requires_partial


def test_super_sub():
    assert split_super_sub("beta_13_2") == ("beta", [], ["13", "2"])
    assert split_super_sub("beta_132_20") == ("beta", [], ["132", "20"])
    assert split_super_sub("beta_13") == ("beta", [], ["13"])
    assert split_super_sub("x_a_b") == ("x", [], ["a", "b"])
    assert split_super_sub("x_1_2_3") == ("x", [], ["1", "2", "3"])
    assert split_super_sub("x_a_b1") == ("x", [], ["a", "b1"])
    assert split_super_sub("x_a_1") == ("x", [], ["a", "1"])
    assert split_super_sub("x_1_a") == ("x", [], ["1", "a"])
    assert split_super_sub("x_1^aa") == ("x", ["aa"], ["1"])
    assert split_super_sub("x_1__aa") == ("x", ["aa"], ["1"])
    assert split_super_sub("x_11^a") == ("x", ["a"], ["11"])
    assert split_super_sub("x_11__a") == ("x", ["a"], ["11"])
    assert split_super_sub("x_a_b_c_d") == ("x", [], ["a", "b", "c", "d"])
    assert split_super_sub("x_a_b^c^d") == ("x", ["c", "d"], ["a", "b"])
    assert split_super_sub("x_a_b__c__d") == ("x", ["c", "d"], ["a", "b"])
    assert split_super_sub("x_a^b_c^d") == ("x", ["b", "d"], ["a", "c"])
    assert split_super_sub("x_a__b_c__d") == ("x", ["b", "d"], ["a", "c"])
    assert split_super_sub("x^a^b_c_d") == ("x", ["a", "b"], ["c", "d"])
    assert split_super_sub("x__a__b_c_d") == ("x", ["a", "b"], ["c", "d"])
    assert split_super_sub("x^a^b^c^d") == ("x", ["a", "b", "c", "d"], [])
    assert split_super_sub("x__a__b__c__d") == ("x", ["a", "b", "c", "d"], [])
    assert split_super_sub("alpha_11") == ("alpha", [], ["11"])
    assert split_super_sub("alpha_11_11") == ("alpha", [], ["11", "11"])
    assert split_super_sub("") == ("", [], [])


def test_requires_partial():
    x, y, z, t, nu = symbols('x y z t nu')
    n = symbols('n', integer=True)

    f = x * y
    assert requires_partial(Derivative(f, x)) is True
    assert requires_partial(Derivative(f, y)) is True

    ## integrating out one of the variables
    assert requires_partial(Derivative(Integral(exp(-x * y), (x, 0, oo)), y, evaluate=False)) is False

    ## bessel function with smooth parameter
    f = besselj(nu, x)
    assert requires_partial(Derivative(f, x)) is True
    assert requires_partial(Derivative(f, nu)) is True

    ## bessel function with integer parameter
    f = besselj(n, x)
    assert requires_partial(Derivative(f, x)) is False
    # this is not really valid (differentiating with respect to an integer)
    # but there's no reason to use the partial derivative symbol there. make
    # sure we don't throw an exception here, though
    assert requires_partial(Derivative(f, n)) is False

    ## bell polynomial
    f = bell(n, x)
    assert requires_partial(Derivative(f, x)) is False
    # again, invalid
    assert requires_partial(Derivative(f, n)) is False

    ## legendre polynomial
    f = legendre(0, x)
    assert requires_partial(Derivative(f, x)) is False

    f = legendre(n, x)
    assert requires_partial(Derivative(f, x)) is False
    # again, invalid
    assert requires_partial(Derivative(f, n)) is False

    f = x ** n
    assert requires_partial(Derivative(f, x)) is False

    assert requires_partial(Derivative(Integral((x*y) ** n * exp(-x * y), (x, 0, oo)), y, evaluate=False)) is False

    # parametric equation
    f = (exp(t), cos(t))
    g = sum(f)
    assert requires_partial(Derivative(g, t)) is False

    # function of unspecified variables
    f = symbols('f', cls=Function)
    assert requires_partial(Derivative(f, x)) is False
    assert requires_partial(Derivative(f, x, y)) is True
