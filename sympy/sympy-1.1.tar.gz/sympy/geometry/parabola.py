"""Parabolic geometrical entity.

Contains
* Parabola

"""

from __future__ import division, print_function
from sympy.core import S
from sympy.core.numbers import oo
from sympy.core.compatibility import ordered
from sympy import symbols, simplify, solve
from sympy.geometry.entity import GeometryEntity, GeometrySet
from sympy.geometry.point import Point, Point2D
from sympy.geometry.line import Line, Line2D, LinearEntity2D, Ray2D, Segment2D, LinearEntity3D
from sympy.geometry.util import _symbol
from sympy.geometry.ellipse import Ellipse


class Parabola(GeometrySet):
    """A parabolic GeometryEntity.

    A parabola is declared with a point, that is called 'focus', and
    a line, that is called 'directrix'.
    Only vertical or horizontal parabolas are currently supported.

    Parameters
    ==========

    focus : Point
        Default value is Point(0, 0)
    directrix : Line

    Attributes
    ==========

    focus
    directrix
    axis of symmetry
    focal length
    p parameter
    vertex
    eccentricity

    Raises
    ======
    ValueError
        When `focus` is not a two dimensional point.
        When `focus` is a point of directrix.
    NotImplementedError
        When `directrix` is neither horizontal nor vertical.

    Examples
    ========

    >>> from sympy import Parabola, Point, Line
    >>> p1 = Parabola(Point(0, 0), Line(Point(5, 8), Point(7,8)))
    >>> p1.focus
    Point2D(0, 0)
    >>> p1.directrix
    Line2D(Point2D(5, 8), Point2D(7, 8))

    """

    def __new__(cls, focus=None, directrix=None, **kwargs):

        if focus:
            focus = Point(focus, dim=2)
        else:
            focus = Point(0, 0)

        directrix = Line(directrix)

        if (directrix.slope != 0 and directrix.slope != S.Infinity):
            raise NotImplementedError('The directrix must be a horizontal'
                                      ' or vertical line')
        if directrix.contains(focus):
            raise ValueError('The focus must not be a point of directrix')

        return GeometryEntity.__new__(cls, focus, directrix, **kwargs)

    @property
    def ambient_dimension(self):
        return S(2)

    @property
    def axis_of_symmetry(self):
        """The axis of symmetry of the parabola.

        Returns
        =======

        axis_of_symmetry : Line

        See Also
        ========

        sympy.geometry.line.Line

        Examples
        ========

        >>> from sympy import Parabola, Point, Line
        >>> p1 = Parabola(Point(0, 0), Line(Point(5, 8), Point(7, 8)))
        >>> p1.axis_of_symmetry
        Line2D(Point2D(0, 0), Point2D(0, 1))

        """
        return self.directrix.perpendicular_line(self.focus)

    @property
    def directrix(self):
        """The directrix of the parabola.

        Returns
        =======

        directrix : Line

        See Also
        ========

        sympy.geometry.line.Line

        Examples
        ========

        >>> from sympy import Parabola, Point, Line
        >>> l1 = Line(Point(5, 8), Point(7, 8))
        >>> p1 = Parabola(Point(0, 0), l1)
        >>> p1.directrix
        Line2D(Point2D(5, 8), Point2D(7, 8))

        """
        return self.args[1]

    @property
    def eccentricity(self):
        """The eccentricity of the parabola.

        Returns
        =======

        eccentricity : number

        A parabola may also be characterized as a conic section with an
        eccentricity of 1. As a consequence of this, all parabolas are
        similar, meaning that while they can be different sizes,
        they are all the same shape.

        See Also
        ========

        https://en.wikipedia.org/wiki/Parabola


        Examples
        ========

        >>> from sympy import Parabola, Point, Line
        >>> p1 = Parabola(Point(0, 0), Line(Point(5, 8), Point(7, 8)))
        >>> p1.eccentricity
        1

        Notes
        -----
        The eccentricity for every Parabola is 1 by definition.

        """
        return S(1)

    def equation(self, x='x', y='y'):
        """The equation of the parabola.

        Parameters
        ==========
        x : str, optional
            Label for the x-axis. Default value is 'x'.
        y : str, optional
            Label for the y-axis. Default value is 'y'.

        Returns
        =======
        equation : sympy expression

        Examples
        ========

        >>> from sympy import Parabola, Point, Line
        >>> p1 = Parabola(Point(0, 0), Line(Point(5, 8), Point(7, 8)))
        >>> p1.equation()
        -x**2 - 16*y + 64
        >>> p1.equation('f')
        -f**2 - 16*y + 64
        >>> p1.equation(y='z')
        -x**2 - 16*z + 64

        """
        x = _symbol(x)
        y = _symbol(y)

        if (self.axis_of_symmetry.slope == 0):
            t1 = 4 * (self.p_parameter) * (x - self.vertex.x)
            t2 = (y - self.vertex.y)**2
        else:
            t1 = 4 * (self.p_parameter) * (y - self.vertex.y)
            t2 = (x - self.vertex.x)**2

        return t1 - t2

    @property
    def focal_length(self):
        """The focal length of the parabola.

        Returns
        =======

        focal_lenght : number or symbolic expression

        Notes
        =====

        The distance between the vertex and the focus
        (or the vertex and directrix), measured along the axis
        of symmetry, is the "focal length".

        See Also
        ========

        https://en.wikipedia.org/wiki/Parabola

        Examples
        ========

        >>> from sympy import Parabola, Point, Line
        >>> p1 = Parabola(Point(0, 0), Line(Point(5, 8), Point(7, 8)))
        >>> p1.focal_length
        4

        """
        distance = self.directrix.distance(self.focus)
        focal_length = distance/2

        return focal_length

    @property
    def focus(self):
        """The focus of the parabola.

        Returns
        =======

        focus : Point

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Parabola, Point, Line
        >>> f1 = Point(0, 0)
        >>> p1 = Parabola(f1, Line(Point(5, 8), Point(7, 8)))
        >>> p1.focus
        Point2D(0, 0)

        """
        return self.args[0]

    def intersection(self, o):
        """The intersection of the parabola and another geometrical entity `o`.

        Parameters
        ==========

        o : GeometryEntity, LinearEntity

        Returns
        =======

        intersection : list of GeometryEntity objects

        Examples
        ========

        >>> from sympy import Parabola, Point, Ellipse, Line, Segment
        >>> p1 = Point(0,0)
        >>> l1 = Line(Point(1, -2), Point(-1,-2))
        >>> parabola1 = Parabola(p1, l1)
        >>> parabola1.intersection(Ellipse(Point(0, 0), 2, 5))
        [Point2D(-2, 0), Point2D(2, 0)]
        >>> parabola1.intersection(Line(Point(-7, 3), Point(12, 3)))
        [Point2D(-4, 3), Point2D(4, 3)]
        >>> parabola1.intersection(Segment((-12, -65), (14, -68)))
        []

        """
        x, y = symbols('x y', real=True)
        parabola_eq = self.equation()
        if isinstance(o, Parabola):
            if o in self:
                return [o]
            else:
                return list(ordered([Point(i) for i in solve([parabola_eq, o.equation()], [x, y])]))
        elif isinstance(o, Point2D):
            if simplify(parabola_eq.subs(([(x, o._args[0]), (y, o._args[1])]))) == 0:
                return [o]
            else:
                return []
        elif isinstance(o, (Segment2D, Ray2D)):
            result = solve([parabola_eq, Line2D(o.points[0], o.points[1]).equation()], [x, y])
            return list(ordered([Point2D(i) for i in result if i in o]))
        elif isinstance(o, (Line2D, Ellipse)):
            return list(ordered([Point2D(i) for i in solve([parabola_eq, o.equation()], [x, y])]))
        elif isinstance(o, LinearEntity3D):
            raise TypeError('Entity must be two dimensional, not three dimensional')
        else:
            raise TypeError('Wrong type of argument were put')

    @property
    def p_parameter(self):
        """P is a parameter of parabola.

        Returns
        =======

        p : number or symbolic expression

        Notes
        =====

        The absolute value of p is the focal length. The sign on p tells
        which way the parabola faces. Vertical parabolas that open up
        and horizontal that open right, give a positive value for p.
        Vertical parabolas that open down and horizontal that open left,
        give a negative value for p.


        See Also
        ========

        http://www.sparknotes.com/math/precalc/conicsections/section2.rhtml

        Examples
        ========

        >>> from sympy import Parabola, Point, Line
        >>> p1 = Parabola(Point(0, 0), Line(Point(5, 8), Point(7, 8)))
        >>> p1.p_parameter
        -4

        """
        if (self.axis_of_symmetry.slope == 0):
            x = -(self.directrix.coefficients[2])
            if (x < self.focus.args[0]):
                p = self.focal_length
            else:
                p = -self.focal_length
        else:
            y = -(self.directrix.coefficients[2])
            if (y > self.focus.args[1]):
                p = -self.focal_length
            else:
                p = self.focal_length

        return p

    @property
    def vertex(self):
        """The vertex of the parabola.

        Returns
        =======

        vertex : Point

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Parabola, Point, Line
        >>> p1 = Parabola(Point(0, 0), Line(Point(5, 8), Point(7, 8)))
        >>> p1.vertex
        Point2D(0, 4)

        """
        focus = self.focus
        if (self.axis_of_symmetry.slope == 0):
            vertex = Point(focus.args[0] - self.p_parameter, focus.args[1])
        else:
            vertex = Point(focus.args[0], focus.args[1] - self.p_parameter)

        return vertex
