from __future__ import division

from sympy import Symbol, pi, symbols, Tuple, S
from sympy.geometry import Curve, Line, Point, Ellipse, Ray, Segment, Circle, Polygon, RegularPolygon
from sympy.utilities.pytest import raises, slow


def test_curve():
    x = Symbol('x', real=True)
    s = Symbol('s')
    z = Symbol('z')

    # this curve is independent of the indicated parameter
    c = Curve([2*s, s**2], (z, 0, 2))

    assert c.parameter == z
    assert c.functions == (2*s, s**2)
    assert c.arbitrary_point() == Point(2*s, s**2)
    assert c.arbitrary_point(z) == Point(2*s, s**2)

    # this is how it is normally used
    c = Curve([2*s, s**2], (s, 0, 2))

    assert c.parameter == s
    assert c.functions == (2*s, s**2)
    t = Symbol('t')
    # the t returned as assumptions
    assert c.arbitrary_point() != Point(2*t, t**2)
    t = Symbol('t', real=True)
    # now t has the same assumptions so the test passes
    assert c.arbitrary_point() == Point(2*t, t**2)
    assert c.arbitrary_point(z) == Point(2*z, z**2)
    assert c.arbitrary_point(c.parameter) == Point(2*s, s**2)
    assert c.arbitrary_point(None) == Point(2*s, s**2)
    assert c.plot_interval() == [t, 0, 2]
    assert c.plot_interval(z) == [z, 0, 2]

    assert Curve([x, x], (x, 0, 1)).rotate(pi/2, (1, 2)).scale(2, 3).translate(
        1, 3).arbitrary_point(s) == \
        Line((0, 0), (1, 1)).rotate(pi/2, (1, 2)).scale(2, 3).translate(
            1, 3).arbitrary_point(s) == \
        Point(-2*s + 7, 3*s + 6)

    raises(ValueError, lambda: Curve((s), (s, 1, 2)))
    raises(ValueError, lambda: Curve((x, x * 2), (1, x)))

    raises(ValueError, lambda: Curve((s, s + t), (s, 1, 2)).arbitrary_point())
    raises(ValueError, lambda: Curve((s, s + t), (t, 1, 2)).arbitrary_point(s))


@slow
def test_free_symbols():
    a, b, c, d, e, f, s = symbols('a:f,s')
    assert Point(a, b).free_symbols == {a, b}
    assert Line((a, b), (c, d)).free_symbols == {a, b, c, d}
    assert Ray((a, b), (c, d)).free_symbols == {a, b, c, d}
    assert Ray((a, b), angle=c).free_symbols == {a, b, c}
    assert Segment((a, b), (c, d)).free_symbols == {a, b, c, d}
    assert Line((a, b), slope=c).free_symbols == {a, b, c}
    assert Curve((a*s, b*s), (s, c, d)).free_symbols == {a, b, c, d}
    assert Ellipse((a, b), c, d).free_symbols == {a, b, c, d}
    assert Ellipse((a, b), c, eccentricity=d).free_symbols == \
        {a, b, c, d}
    assert Ellipse((a, b), vradius=c, eccentricity=d).free_symbols == \
        {a, b, c, d}
    assert Circle((a, b), c).free_symbols == {a, b, c}
    assert Circle((a, b), (c, d), (e, f)).free_symbols == \
        {e, d, c, b, f, a}
    assert Polygon((a, b), (c, d), (e, f)).free_symbols == \
        {e, b, d, f, a, c}
    assert RegularPolygon((a, b), c, d, e).free_symbols == {e, a, b, c, d}


def test_transform():
    x = Symbol('x', real=True)
    y = Symbol('y', real=True)
    c = Curve((x, x**2), (x, 0, 1))
    cout = Curve((2*x - 4, 3*x**2 - 10), (x, 0, 1))
    pts = [Point(0, 0), Point(1/2, 1/4), Point(1, 1)]
    pts_out = [Point(-4, -10), Point(-3, -37/4), Point(-2, -7)]

    assert c.scale(2, 3, (4, 5)) == cout
    assert [c.subs(x, xi/2) for xi in Tuple(0, 1, 2)] == pts
    assert [cout.subs(x, xi/2) for xi in Tuple(0, 1, 2)] == pts_out
    assert Curve((x + y, 3*x), (x, 0, 1)).subs(y, S.Half) == \
        Curve((x + 1/2, 3*x), (x, 0, 1))
    assert Curve((x, 3*x), (x, 0, 1)).translate(4, 5) == \
        Curve((x + 4, 3*x + 5), (x, 0, 1))
