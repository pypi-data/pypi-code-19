"""Line-like geometrical entities.

Contains
========
LinearEntity
Line
Ray
Segment
LinearEntity2D
Line2D
Ray2D
Segment2D
LinearEntity3D
Line3D
Ray3D
Segment3D

"""
from __future__ import division, print_function

from sympy.core import S, sympify
from sympy.core.relational import Eq
from sympy.functions.elementary.trigonometric import (_pi_coeff as pi_coeff, acos, tan)
from sympy.functions.elementary.piecewise import Piecewise
from sympy.logic.boolalg import And
from sympy.simplify.simplify import simplify
from sympy.geometry.exceptions import GeometryError
from sympy.core.decorators import deprecated
from sympy.sets import Intersection
from sympy.matrices import Matrix

from .entity import GeometryEntity, GeometrySet
from .point import Point, Point3D
from .util import _symbol
from sympy.utilities.misc import Undecidable




class LinearEntity(GeometrySet):
    """A base class for all linear entities (Line, Ray and Segment)
    in n-dimensional Euclidean space.

    Attributes
    ==========

    ambient_dimension
    direction
    length
    p1
    p2
    points

    Notes
    =====

    This is an abstract class and is not meant to be instantiated.

    See Also
    ========

    sympy.geometry.entity.GeometryEntity

    """
    def __new__(cls, p1, p2=None, **kwargs):
        p1, p2 = Point._normalize_dimension(p1, p2)
        if p1 == p2:
            # sometimes we return a single point if we are not given two unique
            # points. This is done in the specific subclass
            raise ValueError(
                "%s.__new__ requires two unique Points." % cls.__name__)
        if len(p1) != len(p2):
            raise ValueError(
                "%s.__new__ requires two Points of equal dimension." % cls.__name__)

        return GeometryEntity.__new__(cls, p1, p2, **kwargs)

    def __contains__(self, other):
        """Return a definitive answer or else raise an error if it cannot
        be determined that other is on the boundaries of self."""
        result = self.contains(other)

        if result is not None:
            return result
        else:
            raise Undecidable(
                "can't decide whether '%s' contains '%s'" % (self, other))

    def _span_test(self, other):
        """Test whether the point `other` lies in the positive span of `self`.
        A point x is 'in front' of a point y if x.dot(y) >= 0.  Return
        -1 if `other` is behind `self.p1`, 0 if `other` is `self.p1` and
        and 1 if `other` is in front of `self.p1`."""

        if self.p1 == other:
            return 0

        rel_pos = other - self.p1
        d = self.direction
        if d.dot(rel_pos) > 0:
            return 1
        return -1

    @property
    def ambient_dimension(self):
        return len(self.p1)

    def angle_between(l1, l2):
        """The angle formed between the two linear entities.

        Parameters
        ==========

        l1 : LinearEntity
        l2 : LinearEntity

        Returns
        =======

        angle : angle in radians

        Notes
        =====

        From the dot product of vectors v1 and v2 it is known that:

            ``dot(v1, v2) = |v1|*|v2|*cos(A)``

        where A is the angle formed between the two vectors. We can
        get the directional vectors of the two lines and readily
        find the angle between the two using the above formula.

        See Also
        ========

        is_perpendicular

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2, p3 = Point(0, 0), Point(0, 4), Point(2, 0)
        >>> l1, l2 = Line(p1, p2), Line(p1, p3)
        >>> l1.angle_between(l2)
        pi/2
        >>> from sympy import Point3D, Line3D
        >>> p1, p2, p3 = Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(-1, 2, 0)
        >>> l1, l2 = Line3D(p1, p2), Line3D(p2, p3)
        >>> l1.angle_between(l2)
        acos(-sqrt(2)/3)

        """
        if not isinstance(l1, LinearEntity) and not isinstance(l2, LinearEntity):
            raise TypeError('Must pass only LinearEntity objects')

        v1, v2 = l1.direction, l2.direction
        return acos(v1.dot(v2)/(abs(v1)*abs(v2)))

    def arbitrary_point(self, parameter='t'):
        """A parameterized point on the Line.

        Parameters
        ==========

        parameter : str, optional
            The name of the parameter which will be used for the parametric
            point. The default value is 't'. When this parameter is 0, the
            first point used to define the line will be returned, and when
            it is 1 the second point will be returned.

        Returns
        =======

        point : Point

        Raises
        ======

        ValueError
            When ``parameter`` already appears in the Line's definition.

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(1, 0), Point(5, 3)
        >>> l1 = Line(p1, p2)
        >>> l1.arbitrary_point()
        Point2D(4*t + 1, 3*t)
        >>> from sympy import Point3D, Line3D
        >>> p1, p2 = Point3D(1, 0, 0), Point3D(5, 3, 1)
        >>> l1 = Line3D(p1, p2)
        >>> l1.arbitrary_point()
        Point3D(4*t + 1, 3*t, t)

        """
        t = _symbol(parameter)
        if t.name in (f.name for f in self.free_symbols):
            raise ValueError('Symbol %s already appears in object '
            'and cannot be used as a parameter.' % t.name)
        # multiply on the right so the variable gets
        # combined witht he coordinates of the point
        return self.p1 + (self.p2 - self.p1)*t

    @staticmethod
    def are_concurrent(*lines):
        """Is a sequence of linear entities concurrent?

        Two or more linear entities are concurrent if they all
        intersect at a single point.

        Parameters
        ==========

        lines : a sequence of linear entities.

        Returns
        =======

        True : if the set of linear entities intersect in one point
        False : otherwise.

        See Also
        ========

        sympy.geometry.util.intersection

        Examples
        ========

        >>> from sympy import Point, Line, Line3D
        >>> p1, p2 = Point(0, 0), Point(3, 5)
        >>> p3, p4 = Point(-2, -2), Point(0, 2)
        >>> l1, l2, l3 = Line(p1, p2), Line(p1, p3), Line(p1, p4)
        >>> Line.are_concurrent(l1, l2, l3)
        True
        >>> l4 = Line(p2, p3)
        >>> Line.are_concurrent(l2, l3, l4)
        False
        >>> from sympy import Point3D, Line3D
        >>> p1, p2 = Point3D(0, 0, 0), Point3D(3, 5, 2)
        >>> p3, p4 = Point3D(-2, -2, -2), Point3D(0, 2, 1)
        >>> l1, l2, l3 = Line3D(p1, p2), Line3D(p1, p3), Line3D(p1, p4)
        >>> Line3D.are_concurrent(l1, l2, l3)
        True
        >>> l4 = Line3D(p2, p3)
        >>> Line3D.are_concurrent(l2, l3, l4)
        False

        """

        common_points = Intersection(*lines)
        if common_points.is_FiniteSet and len(common_points) == 1:
            return True
        return False

    def contains(self, other):
        """Subclasses should implement this method and should return
            True if other is on the boundaries of self;
            False if not on the boundaries of self;
            None if a determination cannot be made."""
        raise NotImplementedError()

    @property
    def direction(self):
        """The direction vector of the LinearEntity.

        Returns
        =======

        p : a Point; the ray from the origin to this point is the
            direction of `self`

        Examples
        ========

        >>> from sympy.geometry import Line
        >>> a, b = (1, 1), (1, 3)
        >>> Line(a, b).direction
        Point2D(0, 2)
        >>> Line(b, a).direction
        Point2D(0, -2)

        This can be reported so the distance from the origin is 1:

        >>> Line(b, a).direction.unit
        Point2D(0, -1)

        See Also
        ========

        sympy.geometry.point.Point.unit

        """
        return self.p2 - self.p1

    def intersection(self, other):
        """The intersection with another geometrical entity.

        Parameters
        ==========

        o : Point or LinearEntity

        Returns
        =======

        intersection : list of geometrical entities

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Point, Line, Segment
        >>> p1, p2, p3 = Point(0, 0), Point(1, 1), Point(7, 7)
        >>> l1 = Line(p1, p2)
        >>> l1.intersection(p3)
        [Point2D(7, 7)]
        >>> p4, p5 = Point(5, 0), Point(0, 3)
        >>> l2 = Line(p4, p5)
        >>> l1.intersection(l2)
        [Point2D(15/8, 15/8)]
        >>> p6, p7 = Point(0, 5), Point(2, 6)
        >>> s1 = Segment(p6, p7)
        >>> l1.intersection(s1)
        []
        >>> from sympy import Point3D, Line3D, Segment3D
        >>> p1, p2, p3 = Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(7, 7, 7)
        >>> l1 = Line3D(p1, p2)
        >>> l1.intersection(p3)
        [Point3D(7, 7, 7)]
        >>> l1 = Line3D(Point3D(4,19,12), Point3D(5,25,17))
        >>> l2 = Line3D(Point3D(-3, -15, -19), direction_ratio=[2,8,8])
        >>> l1.intersection(l2)
        [Point3D(1, 1, -3)]
        >>> p6, p7 = Point3D(0, 5, 2), Point3D(2, 6, 3)
        >>> s1 = Segment3D(p6, p7)
        >>> l1.intersection(s1)
        []

        """
        def intersect_parallel_rays(ray1, ray2):
            if ray1.direction.dot(ray2.direction) > 0:
                # rays point in the same direction
                # so return the one that is "in front"
                return [ray2] if ray1._span_test(ray2.p1) >= 0 else [ray1]
            else:
                # rays point in opposite directions
                st = ray1._span_test(ray2.p1)
                if st < 0:
                    return []
                elif st == 0:
                    return [ray2.p1]
                return [Segment(ray1.p1, ray2.p1)]

        def intersect_parallel_ray_and_segment(ray, seg):
            st1, st2 = ray._span_test(seg.p1), ray._span_test(seg.p2)
            if st1 < 0 and st2 < 0:
                return []
            elif st1 >= 0 and st2 >= 0:
                return [seg]
            elif st1 >= 0 and st2 < 0:
                return [Segment(ray.p1, seg.p1)]
            elif st1 <= 0 and st2 > 0:
                return [Segment(ray.p1, seg.p2)]

        def intersect_parallel_segments(seg1, seg2):
            if seg1.contains(seg2):
                return [seg2]
            if seg2.contains(seg1):
                return [seg1]

            # direct the segments so they're oriented the same way
            if seg1.direction.dot(seg2.direction) < 0:
                seg2 = Segment(seg2.p1, seg2.p2)
            # order the segments so seg1 is "behind" seg2
            if seg1._span_test(seg2.p1) < 0:
                seg1, seg2 = seg2, seg1
            if seg2._span_test(seg1.p2) < 0:
                return []
            return [Segment(seg2.p1, seg1.p2)]

        if not isinstance(other, GeometryEntity):
            other = Point(other, dim=self.ambient_dimension)
        if other.is_Point:
            if self.contains(other):
                return [other]
            else:
                return []
        elif isinstance(other, LinearEntity):
            # break into cases based on whether
            # the lines are parallel, non-parallel intersecting, or skew
            pts = Point._normalize_dimension(self.p1, self.p2, other.p1, other.p2)
            rank = Point.affine_rank(*pts)

            if rank == 1:
                # we're collinear
                if isinstance(self, Line):
                    return [other]
                if isinstance(other, Line):
                    return [self]

                if isinstance(self, Ray) and isinstance(other, Ray):
                    return intersect_parallel_rays(self, other)
                if isinstance(self, Ray) and isinstance(other, Segment):
                    return intersect_parallel_ray_and_segment(self, other)
                if isinstance(self, Segment) and isinstance(other, Ray):
                    return intersect_parallel_ray_and_segment(other, self)
                if isinstance(self, Segment) and isinstance(other, Segment):
                    return intersect_parallel_segments(self, other)
            elif rank == 2:
                # we're in the same plane
                l1 = Line(*pts[:2])
                l2 = Line(*pts[2:])

                # check to see if we're parallel.  If we are, we can't
                # be intersecting, since the collinear case was already
                # handled
                if l1.direction.is_scalar_multiple(l2.direction):
                    return []

                # find the intersection as if everything were lines
                # by solving the equation t*d + p1 == s*d' + p1'
                m = Matrix([l1.direction, -l2.direction]).transpose()
                v = Matrix([l2.p1 - l1.p1]).transpose()

                # we cannot use m.solve(v) because that only works for square matrices
                m_rref, pivots = m.col_insert(2, v).rref(simplify=True)
                # rank == 2 ensures we have 2 pivots, but let's check anyway
                if len(pivots) != 2:
                    raise GeometryError("Failed when solving Mx=b when M={} and b={}".format(m,v))
                coeff = m_rref[0,2]
                line_intersection = l1.direction*coeff + self.p1

                # if we're both lines, we can skip a containment check
                if isinstance(self, Line) and isinstance(other, Line):
                    return [line_intersection]

                if self.contains(line_intersection) and other.contains(line_intersection):
                    return [line_intersection]
                return []
            else:
                # we're skew
                return []

        return other.intersection(self)

    def is_parallel(l1, l2):
        """Are two linear entities parallel?

        Parameters
        ==========

        l1 : LinearEntity
        l2 : LinearEntity

        Returns
        =======

        True : if l1 and l2 are parallel,
        False : otherwise.

        See Also
        ========

        coefficients

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(1, 1)
        >>> p3, p4 = Point(3, 4), Point(6, 7)
        >>> l1, l2 = Line(p1, p2), Line(p3, p4)
        >>> Line.is_parallel(l1, l2)
        True
        >>> p5 = Point(6, 6)
        >>> l3 = Line(p3, p5)
        >>> Line.is_parallel(l1, l3)
        False
        >>> from sympy import Point3D, Line3D
        >>> p1, p2 = Point3D(0, 0, 0), Point3D(3, 4, 5)
        >>> p3, p4 = Point3D(2, 1, 1), Point3D(8, 9, 11)
        >>> l1, l2 = Line3D(p1, p2), Line3D(p3, p4)
        >>> Line3D.is_parallel(l1, l2)
        True
        >>> p5 = Point3D(6, 6, 6)
        >>> l3 = Line3D(p3, p5)
        >>> Line3D.is_parallel(l1, l3)
        False

        """

        if not isinstance(l1, LinearEntity) and not isinstance(l2, LinearEntity):
            raise TypeError('Must pass only LinearEntity objects')

        return l1.direction.is_scalar_multiple(l2.direction)

    def is_perpendicular(l1, l2):
        """Are two linear entities perpendicular?

        Parameters
        ==========

        l1 : LinearEntity
        l2 : LinearEntity

        Returns
        =======

        True : if l1 and l2 are perpendicular,
        False : otherwise.

        See Also
        ========

        coefficients

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2, p3 = Point(0, 0), Point(1, 1), Point(-1, 1)
        >>> l1, l2 = Line(p1, p2), Line(p1, p3)
        >>> l1.is_perpendicular(l2)
        True
        >>> p4 = Point(5, 3)
        >>> l3 = Line(p1, p4)
        >>> l1.is_perpendicular(l3)
        False
        >>> from sympy import Point3D, Line3D
        >>> p1, p2, p3 = Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(-1, 2, 0)
        >>> l1, l2 = Line3D(p1, p2), Line3D(p2, p3)
        >>> l1.is_perpendicular(l2)
        False
        >>> p4 = Point3D(5, 3, 7)
        >>> l3 = Line3D(p1, p4)
        >>> l1.is_perpendicular(l3)
        False

        """
        if not isinstance(l1, LinearEntity) and not isinstance(l2, LinearEntity):
            raise TypeError('Must pass only LinearEntity objects')

        return S.Zero.equals(l1.direction.dot(l2.direction))

    def is_similar(self, other):
        """
        Return True if self and other are contained in the same line.

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2, p3 = Point(0, 1), Point(3, 4), Point(2, 3)
        >>> l1 = Line(p1, p2)
        >>> l2 = Line(p1, p3)
        >>> l1.is_similar(l2)
        True
        """
        l = Line(self.p1, self.p2)
        return l.contains(other)

    @property
    def length(self):
        """
        The length of the line.

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(3, 5)
        >>> l1 = Line(p1, p2)
        >>> l1.length
        oo
        """
        return S.Infinity

    @property
    def p1(self):
        """The first defining point of a linear entity.

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(5, 3)
        >>> l = Line(p1, p2)
        >>> l.p1
        Point2D(0, 0)

        """
        return self.args[0]

    @property
    def p2(self):
        """The second defining point of a linear entity.

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(5, 3)
        >>> l = Line(p1, p2)
        >>> l.p2
        Point2D(5, 3)

        """
        return self.args[1]

    def parallel_line(self, p):
        """Create a new Line parallel to this linear entity which passes
        through the point `p`.

        Parameters
        ==========

        p : Point

        Returns
        =======

        line : Line

        See Also
        ========

        is_parallel

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2, p3 = Point(0, 0), Point(2, 3), Point(-2, 2)
        >>> l1 = Line(p1, p2)
        >>> l2 = l1.parallel_line(p3)
        >>> p3 in l2
        True
        >>> l1.is_parallel(l2)
        True
        >>> from sympy import Point3D, Line3D
        >>> p1, p2, p3 = Point3D(0, 0, 0), Point3D(2, 3, 4), Point3D(-2, 2, 0)
        >>> l1 = Line3D(p1, p2)
        >>> l2 = l1.parallel_line(p3)
        >>> p3 in l2
        True
        >>> l1.is_parallel(l2)
        True

        """
        p = Point(p, dim=self.ambient_dimension)
        return Line(p, p + self.direction)

    def perpendicular_line(self, p):
        """Create a new Line perpendicular to this linear entity which passes
        through the point `p`.

        Parameters
        ==========

        p : Point

        Returns
        =======

        line : Line

        See Also
        ========

        is_perpendicular, perpendicular_segment

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2, p3 = Point(0, 0), Point(2, 3), Point(-2, 2)
        >>> l1 = Line(p1, p2)
        >>> l2 = l1.perpendicular_line(p3)
        >>> p3 in l2
        True
        >>> l1.is_perpendicular(l2)
        True
        >>> from sympy import Point3D, Line3D
        >>> p1, p2, p3 = Point3D(0, 0, 0), Point3D(2, 3, 4), Point3D(-2, 2, 0)
        >>> l1 = Line3D(p1, p2)
        >>> l2 = l1.perpendicular_line(p3)
        >>> p3 in l2
        True
        >>> l1.is_perpendicular(l2)
        True

        """
        p = Point(p, dim=self.ambient_dimension)
        if p in self:
            p = p + self.direction.orthogonal_direction
        return Line(p, self.projection(p))

    def perpendicular_segment(self, p):
        """Create a perpendicular line segment from `p` to this line.

        The enpoints of the segment are ``p`` and the closest point in
        the line containing self. (If self is not a line, the point might
        not be in self.)

        Parameters
        ==========

        p : Point

        Returns
        =======

        segment : Segment

        Notes
        =====

        Returns `p` itself if `p` is on this linear entity.

        See Also
        ========

        perpendicular_line

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2, p3 = Point(0, 0), Point(1, 1), Point(0, 2)
        >>> l1 = Line(p1, p2)
        >>> s1 = l1.perpendicular_segment(p3)
        >>> l1.is_perpendicular(s1)
        True
        >>> p3 in s1
        True
        >>> l1.perpendicular_segment(Point(4, 0))
        Segment2D(Point2D(2, 2), Point2D(4, 0))
        >>> from sympy import Point3D, Line3D
        >>> p1, p2, p3 = Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(0, 2, 0)
        >>> l1 = Line3D(p1, p2)
        >>> s1 = l1.perpendicular_segment(p3)
        >>> l1.is_perpendicular(s1)
        True
        >>> p3 in s1
        True
        >>> l1.perpendicular_segment(Point3D(4, 0, 0))
        Segment3D(Point3D(4/3, 4/3, 4/3), Point3D(4, 0, 0))

        """
        p = Point(p, dim=self.ambient_dimension)
        if p in self:
            return p
        l = self.perpendicular_line(p)
        # The intersection should be unique, so unpack the singleton
        p2, = Intersection(Line(self.p1, self.p2), l)

        return Segment(p, p2)

    @property
    def points(self):
        """The two points used to define this linear entity.

        Returns
        =======

        points : tuple of Points

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(5, 11)
        >>> l1 = Line(p1, p2)
        >>> l1.points
        (Point2D(0, 0), Point2D(5, 11))

        """
        return (self.p1, self.p2)

    def projection(self, other):
        """Project a point, line, ray, or segment onto this linear entity.

        Parameters
        ==========

        other : Point or LinearEntity (Line, Ray, Segment)

        Returns
        =======

        projection : Point or LinearEntity (Line, Ray, Segment)
            The return type matches the type of the parameter ``other``.

        Raises
        ======

        GeometryError
            When method is unable to perform projection.

        Notes
        =====

        A projection involves taking the two points that define
        the linear entity and projecting those points onto a
        Line and then reforming the linear entity using these
        projections.
        A point P is projected onto a line L by finding the point
        on L that is closest to P. This point is the intersection
        of L and the line perpendicular to L that passes through P.

        See Also
        ========

        sympy.geometry.point.Point, perpendicular_line

        Examples
        ========

        >>> from sympy import Point, Line, Segment, Rational
        >>> p1, p2, p3 = Point(0, 0), Point(1, 1), Point(Rational(1, 2), 0)
        >>> l1 = Line(p1, p2)
        >>> l1.projection(p3)
        Point2D(1/4, 1/4)
        >>> p4, p5 = Point(10, 0), Point(12, 1)
        >>> s1 = Segment(p4, p5)
        >>> l1.projection(s1)
        Segment2D(Point2D(5, 5), Point2D(13/2, 13/2))
        >>> p1, p2, p3 = Point(0, 0, 1), Point(1, 1, 2), Point(2, 0, 1)
        >>> l1 = Line(p1, p2)
        >>> l1.projection(p3)
        Point3D(2/3, 2/3, 5/3)
        >>> p4, p5 = Point(10, 0, 1), Point(12, 1, 3)
        >>> s1 = Segment(p4, p5)
        >>> l1.projection(s1)
        Segment3D(Point3D(10/3, 10/3, 13/3), Point3D(5, 5, 6))

        """

        if not isinstance(other, GeometryEntity):
            other = Point(other, dim=self.ambient_dimension)

        def proj_point(p):
            return Point.project(p - self.p1, self.direction) + self.p1

        if isinstance(other, Point):
            return proj_point(other)
        elif isinstance(other, LinearEntity):
            p1, p2 = proj_point(other.p1), proj_point(other.p2)
            # test to see if we're degenerate
            if p1 == p2:
                return p1
            projected = other.__class__(p1, p2)
            projected = Intersection(self, projected)
            # if we happen to have intersected in only a point, return that
            if projected.is_FiniteSet and len(projected) == 1:
                # projected is a set of size 1, so unpack it in `a`
                a, = projected
                return a
            return projected

        raise GeometryError(
            "Do not know how to project %s onto %s" % (other, self))

    def random_point(self):
        """A random point on a LinearEntity.

        Returns
        =======

        point : Point

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(5, 3)
        >>> l1 = Line(p1, p2)
        >>> p3 = l1.random_point()
        >>> # random point - don't know its coords in advance
        >>> p3 # doctest: +ELLIPSIS
        Point2D(...)
        >>> # point should belong to the line
        >>> p3 in l1
        True

        """
        from random import randint
        from sympy.functions import floor

        # The lower and upper
        lower, upper = -2**32 - 1, 2**32

        if isinstance(self, Ray):
            lower = 0
        if isinstance(self, Segment):
            lower = 0
            upper = floor(self.length)
        t = randint(lower, upper)

        return self.direction*t/abs(self.direction) + self.p1

class Line(LinearEntity):
    """An infinite line in space.

    A line is declared with two distinct points.
    A 2D line may be declared with a point and slope
    and a 3D line may be defined with a point and a direction ratio.

    Parameters
    ==========

    p1 : Point
    p2 : Point
    slope : sympy expression
    direction_ratio : list

    Notes
    =====

    `Line` will automatically subclass to `Line2D` or `Line3D` based
    on the dimension of `p1`.  The `slope` argument is only relevant
    for `Line2D` and the `direction_ratio` argument is only relevant
    for `Line3D`.

    See Also
    ========

    sympy.geometry.point.Point
    sympy.geometry.line.Line2D
    sympy.geometry.line.Line3D

    Examples
    ========

    >>> import sympy
    >>> from sympy import Point
    >>> from sympy.geometry import Line, Segment
    >>> L = Line(Point(2,3), Point(3,5))
    >>> L
    Line2D(Point2D(2, 3), Point2D(3, 5))
    >>> L.points
    (Point2D(2, 3), Point2D(3, 5))
    >>> L.equation()
    -2*x + y + 1
    >>> L.coefficients
    (-2, 1, 1)

    Instantiate with keyword ``slope``:

    >>> Line(Point(0, 0), slope=0)
    Line2D(Point2D(0, 0), Point2D(1, 0))

    Instantiate with another linear object

    >>> s = Segment((0, 0), (0, 1))
    >>> Line(s).equation()
    x
    """

    def __new__(cls, p1, p2=None, **kwargs):
        if isinstance(p1, LinearEntity):
            if p2:
                raise ValueError('If p1 is a LinearEntity, p2 must be None.')
            dim = len(p1.p1)
        else:
            p1 = Point(p1)
            dim = len(p1)
            if p2 is not None or isinstance(p2, Point) and p2.ambient_dimension != dim:
                p2 = Point(p2)

        if dim == 2:
            return Line2D(p1, p2, **kwargs)
        elif dim == 3:
            return Line3D(p1, p2, **kwargs)
        return LinearEntity.__new__(cls, p1, p2, **kwargs)

    def contains(self, other):
        """
        Return True if `other` is on this Line, or False otherwise.

        Examples
        ========

        >>> from sympy import Line,Point
        >>> p1, p2 = Point(0, 1), Point(3, 4)
        >>> l = Line(p1, p2)
        >>> l.contains(p1)
        True
        >>> l.contains((0, 1))
        True
        >>> l.contains((0, 0))
        False
        >>> a = (0, 0, 0)
        >>> b = (1, 1, 1)
        >>> c = (2, 2, 2)
        >>> l1 = Line(a, b)
        >>> l2 = Line(b, a)
        >>> l1 == l2
        False
        >>> l1 in l2
        True

        """
        if not isinstance(other, GeometryEntity):
            other = Point(other, dim=self.ambient_dimension)
        if isinstance(other, Point):
            return Point.is_collinear(other, self.p1, self.p2)
        if isinstance(other, LinearEntity):
            return Point.is_collinear(self.p1, self.p2, other.p1, other.p2)
        return False

    def distance(self, other):
        """
        Finds the shortest distance between a line and a point.

        Raises
        ======

        NotImplementedError is raised if `other` is not a Point

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(1, 1)
        >>> s = Line(p1, p2)
        >>> s.distance(Point(-1, 1))
        sqrt(2)
        >>> s.distance((-1, 2))
        3*sqrt(2)/2
        >>> p1, p2 = Point(0, 0, 0), Point(1, 1, 1)
        >>> s = Line(p1, p2)
        >>> s.distance(Point(-1, 1, 1))
        2*sqrt(6)/3
        >>> s.distance((-1, 1, 1))
        2*sqrt(6)/3

        """
        if not isinstance(other, GeometryEntity):
            other = Point(other, dim=self.ambient_dimension)
        if self.contains(other):
            return S.Zero
        return self.perpendicular_segment(other).length

    @deprecated(useinstead="equals", issue=12860, deprecated_since_version="1.0")
    def equal(self, other):
        return self.equals(other)

    def equals(self, other):
        """Returns True if self and other are the same mathematical entities"""
        if not isinstance(other, Line):
            return False
        return Point.is_collinear(self.p1, other.p1, self.p2, other.p2)

    def plot_interval(self, parameter='t'):
        """The plot interval for the default geometric plot of line. Gives
        values that will produce a line that is +/- 5 units long (where a
        unit is the distance between the two points that define the line).

        Parameters
        ==========

        parameter : str, optional
            Default value is 't'.

        Returns
        =======

        plot_interval : list (plot interval)
            [parameter, lower_bound, upper_bound]

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(5, 3)
        >>> l1 = Line(p1, p2)
        >>> l1.plot_interval()
        [t, -5, 5]

        """
        t = _symbol(parameter)
        return [t, -5, 5]

class Ray(LinearEntity):
    """A Ray is a semi-line in the space with a source point and a direction.

    Parameters
    ==========

    p1 : Point
        The source of the Ray
    p2 : Point or radian value
        This point determines the direction in which the Ray propagates.
        If given as an angle it is interpreted in radians with the positive
        direction being ccw.

    Attributes
    ==========

    source

    See Also
    ========

    sympy.geometry.line.Ray2D
    sympy.geometry.line.Ray3D
    sympy.geometry.point.Point
    sympy.geometry.line.Line

    Notes
    =====

    `Ray` will automatically subclass to `Ray2D` or `Ray3D` based on the
    dimension of `p1`.

    Examples
    ========

    >>> import sympy
    >>> from sympy import Point, pi
    >>> from sympy.geometry import Ray
    >>> r = Ray(Point(2, 3), Point(3, 5))
    >>> r
    Ray2D(Point2D(2, 3), Point2D(3, 5))
    >>> r.points
    (Point2D(2, 3), Point2D(3, 5))
    >>> r.source
    Point2D(2, 3)
    >>> r.xdirection
    oo
    >>> r.ydirection
    oo
    >>> r.slope
    2
    >>> Ray(Point(0, 0), angle=pi/4).slope
    1

    """
    def __new__(cls, p1, p2=None, **kwargs):
        p1 = Point(p1)
        if p2 is not None:
            p1, p2 = Point._normalize_dimension(p1, Point(p2))
        dim = len(p1)

        if dim == 2:
            return Ray2D(p1, p2, **kwargs)
        elif dim == 3:
            return Ray3D(p1, p2, **kwargs)
        return LinearEntity.__new__(cls, p1, *pts, **kwargs)

    def _svg(self, scale_factor=1., fill_color="#66cc99"):
        """Returns SVG path element for the LinearEntity.

        Parameters
        ==========

        scale_factor : float
            Multiplication factor for the SVG stroke-width.  Default is 1.
        fill_color : str, optional
            Hex string for fill color. Default is "#66cc99".
        """

        from sympy.core.evalf import N

        verts = (N(self.p1), N(self.p2))
        coords = ["{0},{1}".format(p.x, p.y) for p in verts]
        path = "M {0} L {1}".format(coords[0], " L ".join(coords[1:]))

        return (
            '<path fill-rule="evenodd" fill="{2}" stroke="#555555" '
            'stroke-width="{0}" opacity="0.6" d="{1}" '
            'marker-start="url(#markerCircle)" marker-end="url(#markerArrow)"/>'
            ).format(2. * scale_factor, path, fill_color)

    def contains(self, other):
        """
        Is other GeometryEntity contained in this Ray?

        Examples
        ========

        >>> from sympy import Ray,Point,Segment
        >>> p1, p2 = Point(0, 0), Point(4, 4)
        >>> r = Ray(p1, p2)
        >>> r.contains(p1)
        True
        >>> r.contains((1, 1))
        True
        >>> r.contains((1, 3))
        False
        >>> s = Segment((1, 1), (2, 2))
        >>> r.contains(s)
        True
        >>> s = Segment((1, 2), (2, 5))
        >>> r.contains(s)
        False
        >>> r1 = Ray((2, 2), (3, 3))
        >>> r.contains(r1)
        True
        >>> r1 = Ray((2, 2), (3, 5))
        >>> r.contains(r1)
        False
        """
        if not isinstance(other, GeometryEntity):
            other = Point(other, dim=self.ambient_dimension)
        if isinstance(other, Point):
            if Point.is_collinear(self.p1, self.p2, other):
                # if we're in the direction of the ray, our
                # direction vector dot the ray's direction vector
                # should be non-negative
                return bool( (self.p2 - self.p1).dot(other - self.p1) >= S.Zero )
            return False
        elif isinstance(other, Ray):
            if Point.is_collinear(self.p1, self.p2, other.p1, other.p2):
                return bool( (self.p2 - self.p1).dot(other.p2 - other.p1) > S.Zero )
            return False
        elif isinstance(other, Segment):
            return other.p1 in self and other.p2 in self

        # No other known entity can be contained in a Ray
        return False

    def distance(self, other):
        """
        Finds the shortest distance between the ray and a point.

        Raises
        ======

        NotImplementedError is raised if `other` is not a Point

        Examples
        ========

        >>> from sympy import Point, Ray
        >>> p1, p2 = Point(0, 0), Point(1, 1)
        >>> s = Ray(p1, p2)
        >>> s.distance(Point(-1, -1))
        sqrt(2)
        >>> s.distance((-1, 2))
        3*sqrt(2)/2
        >>> p1, p2 = Point(0, 0, 0), Point(1, 1, 2)
        >>> s = Ray(p1, p2)
        >>> s
        Ray3D(Point3D(0, 0, 0), Point3D(1, 1, 2))
        >>> s.distance(Point(-1, -1, 2))
        4*sqrt(3)/3
        >>> s.distance((-1, -1, 2))
        4*sqrt(3)/3

        """
        if not isinstance(other, GeometryEntity):
            other = Point(other, dim=self.ambient_dimension)
        if self.contains(other):
            return S.Zero

        proj = Line(self.p1, self.p2).projection(other)
        if self.contains(proj):
            return abs(other - proj)
        else:
            return abs(other - self.source)

    def equals(self, other):
        """Returns True if self and other are the same mathematical entities"""
        if not isinstance(other, Ray):
            return False
        return self.source == other.source and other.p2 in self

    def plot_interval(self, parameter='t'):
        """The plot interval for the default geometric plot of the Ray. Gives
        values that will produce a ray that is 10 units long (where a unit is
        the distance between the two points that define the ray).

        Parameters
        ==========

        parameter : str, optional
            Default value is 't'.

        Returns
        =======

        plot_interval : list
            [parameter, lower_bound, upper_bound]

        Examples
        ========

        >>> from sympy import Point, Ray, pi
        >>> r = Ray((0, 0), angle=pi/4)
        >>> r.plot_interval()
        [t, 0, 10]

        """
        t = _symbol(parameter)
        return [t, 0, 10]

    @property
    def source(self):
        """The point from which the ray emanates.

        See Also
        ========

        sympy.geometry.point.Point

        Examples
        ========

        >>> from sympy import Point, Ray
        >>> p1, p2 = Point(0, 0), Point(4, 1)
        >>> r1 = Ray(p1, p2)
        >>> r1.source
        Point2D(0, 0)
        >>> p1, p2 = Point(0, 0, 0), Point(4, 1, 5)
        >>> r1 = Ray(p2, p1)
        >>> r1.source
        Point3D(4, 1, 5)

        """
        return self.p1

class Segment(LinearEntity):
    """An undirected line segment in space.

    Parameters
    ==========

    p1 : Point
    p2 : Point

    Attributes
    ==========

    length : number or sympy expression
    midpoint : Point

    See Also
    ========

    sympy.geometry.line.Segment2D
    sympy.geometry.line.Segment3D
    sympy.geometry.point.Point
    sympy.geometry.line.Line

    Notes
    =====

    If 2D or 3D points are used to define `Segment`, it will
    be automatically subclassed to `Segment2D` or `Segment3D`.

    Examples
    ========

    >>> import sympy
    >>> from sympy import Point
    >>> from sympy.geometry import Segment
    >>> Segment((1, 0), (1, 1)) # tuples are interpreted as pts
    Segment2D(Point2D(1, 0), Point2D(1, 1))
    >>> s = Segment(Point(4, 3), Point(1, 1))
    >>> s
    Segment2D(Point2D(1, 1), Point2D(4, 3))
    >>> s.points
    (Point2D(1, 1), Point2D(4, 3))
    >>> s.slope
    2/3
    >>> s.length
    sqrt(13)
    >>> s.midpoint
    Point2D(5/2, 2)
    >>> Segment((1, 0, 0), (1, 1, 1)) # tuples are interpreted as pts
    Segment3D(Point3D(1, 0, 0), Point3D(1, 1, 1))
    >>> s = Segment(Point(4, 3, 9), Point(1, 1, 7))
    >>> s
    Segment3D(Point3D(1, 1, 7), Point3D(4, 3, 9))
    >>> s.points
    (Point3D(1, 1, 7), Point3D(4, 3, 9))
    >>> s.length
    sqrt(17)
    >>> s.midpoint
    Point3D(5/2, 2, 8)

    """
    def __new__(cls, p1, p2, **kwargs):
        p1, p2 = Point._normalize_dimension(Point(p1), Point(p2))
        dim = len(p1)

        if dim == 2:
            return Segment2D(p1, p2, **kwargs)
        elif dim == 3:
            return Segment3D(p1, p2, **kwargs)
        return LinearEntity.__new__(cls, p1, p2, **kwargs)

    def contains(self, other):
        """
        Is the other GeometryEntity contained within this Segment?

        Examples
        ========

        >>> from sympy import Point, Segment
        >>> p1, p2 = Point(0, 1), Point(3, 4)
        >>> s = Segment(p1, p2)
        >>> s2 = Segment(p2, p1)
        >>> s.contains(s2)
        True
        >>> from sympy import Point3D, Segment3D
        >>> p1, p2 = Point3D(0, 1, 1), Point3D(3, 4, 5)
        >>> s = Segment3D(p1, p2)
        >>> s2 = Segment3D(p2, p1)
        >>> s.contains(s2)
        True
        >>> s.contains((p1 + p2) / 2)
        True
        """

        if not isinstance(other, GeometryEntity):
            other = Point(other, dim=self.ambient_dimension)
        if isinstance(other, Point):
            if Point.is_collinear(other, self.p1, self.p2):
                d1, d2 = other - self.p1, other - self.p2
                d = self.p2 - self.p1
                # without the call to simplify, sympy cannot tell that an expression
                # like (a+b)*(a/2+b/2) is always non-negative.  If it cannot be
                # determined, raise an Undecidable error
                try:
                    # the triangle inequality says that |d1|+|d2| >= |d| and is strict
                    # only if other lies in the line segment
                    return bool(Eq(simplify(abs(d1) + abs(d2) - abs(d)), 0))
                except TypeError:
                    raise Undecidable("Cannot determine if {} is in {}".format(other, self))
        if isinstance(other, Segment):
            return other.p1 in self and other.p2 in self

        return False

    def distance(self, other):
        """
        Finds the shortest distance between a line segment and a point.

        Raises
        ======

        NotImplementedError is raised if `other` is not a Point

        Examples
        ========

        >>> from sympy import Point, Segment
        >>> p1, p2 = Point(0, 1), Point(3, 4)
        >>> s = Segment(p1, p2)
        >>> s.distance(Point(10, 15))
        sqrt(170)
        >>> s.distance((0, 12))
        sqrt(73)
        >>> from sympy import Point3D, Segment3D
        >>> p1, p2 = Point3D(0, 0, 3), Point3D(1, 1, 4)
        >>> s = Segment3D(p1, p2)
        >>> s.distance(Point3D(10, 15, 12))
        sqrt(341)
        >>> s.distance((10, 15, 12))
        sqrt(341)
        """
        if not isinstance(other, GeometryEntity):
            other = Point(other, dim=self.ambient_dimension)
        if isinstance(other, Point):
            vp1 = other - self.p1
            vp2 = other - self.p2

            dot_prod_sign_1 = self.direction.dot(vp1) >= 0
            dot_prod_sign_2 = self.direction.dot(vp2) <= 0
            if dot_prod_sign_1 and dot_prod_sign_2:
                return Line(self.p1, self.p2).distance(other)
            if dot_prod_sign_1 and not dot_prod_sign_2:
                return abs(vp2)
            if not dot_prod_sign_1 and dot_prod_sign_2:
                return abs(vp1)
        raise NotImplementedError()

    @property
    def length(self):
        """The length of the line segment.

        See Also
        ========

        sympy.geometry.point.Point.distance

        Examples
        ========

        >>> from sympy import Point, Segment
        >>> p1, p2 = Point(0, 0), Point(4, 3)
        >>> s1 = Segment(p1, p2)
        >>> s1.length
        5
        >>> from sympy import Point3D, Segment3D
        >>> p1, p2 = Point3D(0, 0, 0), Point3D(4, 3, 3)
        >>> s1 = Segment3D(p1, p2)
        >>> s1.length
        sqrt(34)

        """
        return Point.distance(self.p1, self.p2)

    @property
    def midpoint(self):
        """The midpoint of the line segment.

        See Also
        ========

        sympy.geometry.point.Point.midpoint

        Examples
        ========

        >>> from sympy import Point, Segment
        >>> p1, p2 = Point(0, 0), Point(4, 3)
        >>> s1 = Segment(p1, p2)
        >>> s1.midpoint
        Point2D(2, 3/2)
        >>> from sympy import Point3D, Segment3D
        >>> p1, p2 = Point3D(0, 0, 0), Point3D(4, 3, 3)
        >>> s1 = Segment3D(p1, p2)
        >>> s1.midpoint
        Point3D(2, 3/2, 3/2)

        """
        return Point.midpoint(self.p1, self.p2)

    def perpendicular_bisector(self, p=None):
        """The perpendicular bisector of this segment.

        If no point is specified or the point specified is not on the
        bisector then the bisector is returned as a Line. Otherwise a
        Segment is returned that joins the point specified and the
        intersection of the bisector and the segment.

        Parameters
        ==========

        p : Point

        Returns
        =======

        bisector : Line or Segment

        See Also
        ========

        LinearEntity.perpendicular_segment

        Examples
        ========

        >>> from sympy import Point, Segment
        >>> p1, p2, p3 = Point(0, 0), Point(6, 6), Point(5, 1)
        >>> s1 = Segment(p1, p2)
        >>> s1.perpendicular_bisector()
        Line2D(Point2D(3, 3), Point2D(-3, 9))

        >>> s1.perpendicular_bisector(p3)
        Segment2D(Point2D(3, 3), Point2D(5, 1))

        """
        l = self.perpendicular_line(self.midpoint)
        if p is not None:
            p2 = Point(p, dim=self.ambient_dimension)
            if p2 in l:
                return Segment(self.midpoint, p2)
        return l

    def plot_interval(self, parameter='t'):
        """The plot interval for the default geometric plot of the Segment gives
        values that will produce the full segment in a plot.

        Parameters
        ==========

        parameter : str, optional
            Default value is 't'.

        Returns
        =======

        plot_interval : list
            [parameter, lower_bound, upper_bound]

        Examples
        ========

        >>> from sympy import Point, Segment
        >>> p1, p2 = Point(0, 0), Point(5, 3)
        >>> s1 = Segment(p1, p2)
        >>> s1.plot_interval()
        [t, 0, 1]

        """
        t = _symbol(parameter)
        return [t, 0, 1]

class LinearEntity2D(LinearEntity):
    """A base class for all linear entities (line, ray and segment)
    in a 2-dimensional Euclidean space.

    Attributes
    ==========

    p1
    p2
    coefficients
    slope
    points

    Notes
    =====

    This is an abstract class and is not meant to be instantiated.

    See Also
    ========

    sympy.geometry.entity.GeometryEntity

    """
    @property
    def bounds(self):
        """Return a tuple (xmin, ymin, xmax, ymax) representing the bounding
        rectangle for the geometric figure.

        """

        verts = self.points
        xs = [p.x for p in verts]
        ys = [p.y for p in verts]
        return (min(xs), min(ys), max(xs), max(ys))

    def perpendicular_line(self, p):
        """Create a new Line perpendicular to this linear entity which passes
        through the point `p`.

        Parameters
        ==========

        p : Point

        Returns
        =======

        line : Line

        See Also
        ========

        is_perpendicular, perpendicular_segment

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2, p3 = Point(0, 0), Point(2, 3), Point(-2, 2)
        >>> l1 = Line(p1, p2)
        >>> l2 = l1.perpendicular_line(p3)
        >>> p3 in l2
        True
        >>> l1.is_perpendicular(l2)
        True

        """
        p = Point(p, dim=self.ambient_dimension)
        # any two lines in R^2 intersect, so blindly making
        # a line through p in an orthogonal direction will work
        return Line(p, p + self.direction.orthogonal_direction)

    @property
    def slope(self):
        """The slope of this linear entity, or infinity if vertical.

        Returns
        =======

        slope : number or sympy expression

        See Also
        ========

        coefficients

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(0, 0), Point(3, 5)
        >>> l1 = Line(p1, p2)
        >>> l1.slope
        5/3

        >>> p3 = Point(0, 4)
        >>> l2 = Line(p1, p3)
        >>> l2.slope
        oo

        """
        d1, d2 = (self.p1 - self.p2).args
        if d1 == 0:
            return S.Infinity
        return simplify(d2/d1)

class Line2D(LinearEntity2D, Line):
    """An infinite line in space 2D.

    A line is declared with two distinct points or a point and slope
    as defined using keyword `slope`.

    Parameters
    ==========

    p1 : Point
    pt : Point
    slope : sympy expression

    See Also
    ========

    sympy.geometry.point.Point

    Examples
    ========

    >>> import sympy
    >>> from sympy import Point
    >>> from sympy.abc import L
    >>> from sympy.geometry import Line, Segment
    >>> L = Line(Point(2,3), Point(3,5))
    >>> L
    Line2D(Point2D(2, 3), Point2D(3, 5))
    >>> L.points
    (Point2D(2, 3), Point2D(3, 5))
    >>> L.equation()
    -2*x + y + 1
    >>> L.coefficients
    (-2, 1, 1)

    Instantiate with keyword ``slope``:

    >>> Line(Point(0, 0), slope=0)
    Line2D(Point2D(0, 0), Point2D(1, 0))

    Instantiate with another linear object

    >>> s = Segment((0, 0), (0, 1))
    >>> Line(s).equation()
    x
    """
    def __new__(cls, p1, pt=None, slope=None, **kwargs):
        if isinstance(p1, LinearEntity):
            if pt is not None:
                raise ValueError('When p1 is a LinearEntity, pt should be None')
            p1, pt = Point._normalize_dimension(*p1.args, dim=2)
        else:
            p1 = Point(p1, dim=2)
        if pt is not None and slope is None:
            try:
                p2 = Point(pt, dim=2)
            except (NotImplementedError, TypeError, ValueError):
                raise ValueError('The 2nd argument was not a valid Point. '
                'If it was a slope, enter it with keyword "slope".')
        elif slope is not None and pt is None:
            slope = sympify(slope)
            if slope.is_finite is False:
                # when infinite slope, don't change x
                dx = 0
                dy = 1
            else:
                # go over 1 up slope
                dx = 1
                dy = slope
            # XXX avoiding simplification by adding to coords directly
            p2 = Point(p1.x + dx, p1.y + dy, evaluate=False)
        else:
            raise ValueError('A 2nd Point or keyword "slope" must be used.')
        return LinearEntity2D.__new__(cls, p1, p2, **kwargs)

    def _svg(self, scale_factor=1., fill_color="#66cc99"):
        """Returns SVG path element for the LinearEntity.

        Parameters
        ==========

        scale_factor : float
            Multiplication factor for the SVG stroke-width.  Default is 1.
        fill_color : str, optional
            Hex string for fill color. Default is "#66cc99".
        """

        from sympy.core.evalf import N

        verts = (N(self.p1), N(self.p2))
        coords = ["{0},{1}".format(p.x, p.y) for p in verts]
        path = "M {0} L {1}".format(coords[0], " L ".join(coords[1:]))

        return (
            '<path fill-rule="evenodd" fill="{2}" stroke="#555555" '
            'stroke-width="{0}" opacity="0.6" d="{1}" '
            'marker-start="url(#markerReverseArrow)" marker-end="url(#markerArrow)"/>'
            ).format(2. * scale_factor, path, fill_color)

    @property
    def coefficients(self):
        """The coefficients (`a`, `b`, `c`) for `ax + by + c = 0`.

        See Also
        ========

        sympy.geometry.line.Line.equation

        Examples
        ========

        >>> from sympy import Point, Line
        >>> from sympy.abc import x, y
        >>> p1, p2 = Point(0, 0), Point(5, 3)
        >>> l = Line(p1, p2)
        >>> l.coefficients
        (-3, 5, 0)

        >>> p3 = Point(x, y)
        >>> l2 = Line(p1, p3)
        >>> l2.coefficients
        (-y, x, 0)

        """
        p1, p2 = self.points
        if p1.x == p2.x:
            return (S.One, S.Zero, -p1.x)
        elif p1.y == p2.y:
            return (S.Zero, S.One, -p1.y)
        return tuple([simplify(i) for i in
               (self.p1.y - self.p2.y,
                self.p2.x - self.p1.x,
                self.p1.x*self.p2.y - self.p1.y*self.p2.x)])

    def equation(self, x='x', y='y'):
        """The equation of the line: ax + by + c.

        Parameters
        ==========

        x : str, optional
            The name to use for the x-axis, default value is 'x'.
        y : str, optional
            The name to use for the y-axis, default value is 'y'.

        Returns
        =======

        equation : sympy expression

        See Also
        ========

        LinearEntity.coefficients

        Examples
        ========

        >>> from sympy import Point, Line
        >>> p1, p2 = Point(1, 0), Point(5, 3)
        >>> l1 = Line(p1, p2)
        >>> l1.equation()
        -3*x + 4*y + 3

        """
        x, y = _symbol(x), _symbol(y)
        p1, p2 = self.points
        if p1.x == p2.x:
            return x - p1.x
        elif p1.y == p2.y:
            return y - p1.y

        a, b, c = self.coefficients
        return a*x + b*y + c

class Ray2D(LinearEntity2D, Ray):
    """
    A Ray is a semi-line in the space with a source point and a direction.

    Parameters
    ==========

    p1 : Point
        The source of the Ray
    p2 : Point or radian value
        This point determines the direction in which the Ray propagates.
        If given as an angle it is interpreted in radians with the positive
        direction being ccw.

    Attributes
    ==========

    source
    xdirection
    ydirection

    See Also
    ========

    sympy.geometry.point.Point, Line

    Examples
    ========

    >>> import sympy
    >>> from sympy import Point, pi
    >>> from sympy.geometry import Ray
    >>> r = Ray(Point(2, 3), Point(3, 5))
    >>> r
    Ray2D(Point2D(2, 3), Point2D(3, 5))
    >>> r.points
    (Point2D(2, 3), Point2D(3, 5))
    >>> r.source
    Point2D(2, 3)
    >>> r.xdirection
    oo
    >>> r.ydirection
    oo
    >>> r.slope
    2
    >>> Ray(Point(0, 0), angle=pi/4).slope
    1

    """
    def __new__(cls, p1, pt=None, angle=None, **kwargs):
        p1 = Point(p1, dim=2)
        if pt is not None and angle is None:
            try:
                p2 = Point(pt, dim=2)
            except (NotImplementedError, TypeError, ValueError):
                from sympy.utilities.misc import filldedent
                raise ValueError(filldedent('''
                    The 2nd argument was not a valid Point; if
                    it was meant to be an angle it should be
                    given with keyword "angle".'''))
            if p1 == p2:
                raise ValueError('A Ray requires two distinct points.')
        elif angle is not None and pt is None:
            # we need to know if the angle is an odd multiple of pi/2
            c = pi_coeff(sympify(angle))
            p2 = None
            if c is not None:
                if c.is_Rational:
                    if c.q == 2:
                        if c.p == 1:
                            p2 = p1 + Point(0, 1)
                        elif c.p == 3:
                            p2 = p1 + Point(0, -1)
                    elif c.q == 1:
                        if c.p == 0:
                            p2 = p1 + Point(1, 0)
                        elif c.p == 1:
                            p2 = p1 + Point(-1, 0)
                if p2 is None:
                    c *= S.Pi
            else:
                c = angle % (2*S.Pi)
            if not p2:
                m = 2*c/S.Pi
                left = And(1 < m, m < 3)  # is it in quadrant 2 or 3?
                x = Piecewise((-1, left), (Piecewise((0, Eq(m % 1, 0)), (1, True)), True))
                y = Piecewise((-tan(c), left), (Piecewise((1, Eq(m, 1)), (-1, Eq(m, 3)), (tan(c), True)), True))
                p2 = p1 + Point(x, y)
        else:
            raise ValueError('A 2nd point or keyword "angle" must be used.')

        return LinearEntity2D.__new__(cls, p1, p2, **kwargs)

    @property
    def xdirection(self):
        """The x direction of the ray.

        Positive infinity if the ray points in the positive x direction,
        negative infinity if the ray points in the negative x direction,
        or 0 if the ray is vertical.

        See Also
        ========

        ydirection

        Examples
        ========

        >>> from sympy import Point, Ray
        >>> p1, p2, p3 = Point(0, 0), Point(1, 1), Point(0, -1)
        >>> r1, r2 = Ray(p1, p2), Ray(p1, p3)
        >>> r1.xdirection
        oo
        >>> r2.xdirection
        0

        """
        if self.p1.x < self.p2.x:
            return S.Infinity
        elif self.p1.x == self.p2.x:
            return S.Zero
        else:
            return S.NegativeInfinity

    @property
    def ydirection(self):
        """The y direction of the ray.

        Positive infinity if the ray points in the positive y direction,
        negative infinity if the ray points in the negative y direction,
        or 0 if the ray is horizontal.

        See Also
        ========

        xdirection

        Examples
        ========

        >>> from sympy import Point, Ray
        >>> p1, p2, p3 = Point(0, 0), Point(-1, -1), Point(-1, 0)
        >>> r1, r2 = Ray(p1, p2), Ray(p1, p3)
        >>> r1.ydirection
        -oo
        >>> r2.ydirection
        0

        """
        if self.p1.y < self.p2.y:
            return S.Infinity
        elif self.p1.y == self.p2.y:
            return S.Zero
        else:
            return S.NegativeInfinity

class Segment2D(LinearEntity2D, Segment):
    """An undirected line segment in 2D space.

    Parameters
    ==========

    p1 : Point
    p2 : Point

    Attributes
    ==========

    length : number or sympy expression
    midpoint : Point

    See Also
    ========

    sympy.geometry.point.Point, Line

    Examples
    ========

    >>> import sympy
    >>> from sympy import Point
    >>> from sympy.geometry import Segment
    >>> Segment((1, 0), (1, 1)) # tuples are interpreted as pts
    Segment2D(Point2D(1, 0), Point2D(1, 1))
    >>> s = Segment(Point(4, 3), Point(1, 1))
    >>> s
    Segment2D(Point2D(1, 1), Point2D(4, 3))
    >>> s.points
    (Point2D(1, 1), Point2D(4, 3))
    >>> s.slope
    2/3
    >>> s.length
    sqrt(13)
    >>> s.midpoint
    Point2D(5/2, 2)

    """
    def __new__(cls, p1, p2, **kwargs):
        # Reorder the two points under the following ordering:
        #   if p1.x != p2.x then p1.x < p2.x
        #   if p1.x == p2.x then p1.y < p2.y
        p1 = Point(p1, dim=2)
        p2 = Point(p2, dim=2)
        if p1 == p2:
            return p1
        if (p1.x > p2.x) == True:
            p1, p2 = p2, p1
        elif (p1.x == p2.x) == True and (p1.y > p2.y) == True:
            p1, p2 = p2, p1
        return LinearEntity2D.__new__(cls, p1, p2, **kwargs)

    def _svg(self, scale_factor=1., fill_color="#66cc99"):
        """Returns SVG path element for the LinearEntity.

        Parameters
        ==========

        scale_factor : float
            Multiplication factor for the SVG stroke-width.  Default is 1.
        fill_color : str, optional
            Hex string for fill color. Default is "#66cc99".
        """

        from sympy.core.evalf import N

        verts = (N(self.p1), N(self.p2))
        coords = ["{0},{1}".format(p.x, p.y) for p in verts]
        path = "M {0} L {1}".format(coords[0], " L ".join(coords[1:]))
        return (
            '<path fill-rule="evenodd" fill="{2}" stroke="#555555" '
            'stroke-width="{0}" opacity="0.6" d="{1}" />'
            ).format(2. * scale_factor, path, fill_color)

class LinearEntity3D(LinearEntity):
    """An base class for all linear entities (line, ray and segment)
    in a 3-dimensional Euclidean space.

    Attributes
    ==========

    p1
    p2
    direction_ratio
    direction_cosine
    points

    Notes
    =====

    This is a base class and is not meant to be instantiated.
    """

    def __new__(cls, p1, p2, **kwargs):
        p1 = Point3D(p1, dim=3)
        p2 = Point3D(p2, dim=3)
        if p1 == p2:
            # if it makes sense to return a Point, handle in subclass
            raise ValueError(
                "%s.__new__ requires two unique Points." % cls.__name__)

        return GeometryEntity.__new__(cls, p1, p2, **kwargs)

    ambient_dimension = 3

    @property
    def direction_ratio(self):
        """The direction ratio of a given line in 3D.

        See Also
        ========

        sympy.geometry.line.Line.equation

        Examples
        ========

        >>> from sympy import Point3D, Line3D
        >>> p1, p2 = Point3D(0, 0, 0), Point3D(5, 3, 1)
        >>> l = Line3D(p1, p2)
        >>> l.direction_ratio
        [5, 3, 1]
        """
        p1, p2 = self.points
        return p1.direction_ratio(p2)

    @property
    def direction_cosine(self):
        """The normalized direction ratio of a given line in 3D.

        See Also
        ========

        sympy.geometry.line.Line.equation

        Examples
        ========

        >>> from sympy import Point3D, Line3D
        >>> p1, p2 = Point3D(0, 0, 0), Point3D(5, 3, 1)
        >>> l = Line3D(p1, p2)
        >>> l.direction_cosine
        [sqrt(35)/7, 3*sqrt(35)/35, sqrt(35)/35]
        >>> sum(i**2 for i in _)
        1
        """
        p1, p2 = self.points
        return p1.direction_cosine(p2)

class Line3D(LinearEntity3D, Line):
    """An infinite 3D line in space.

    A line is declared with two distinct points or a point and direction_ratio
    as defined using keyword `direction_ratio`.

    Parameters
    ==========

    p1 : Point3D
    pt : Point3D
    direction_ratio : list

    See Also
    ========

    sympy.geometry.point.Point3D
    sympy.geometry.line.Line
    sympy.geometry.line.Line2D

    Examples
    ========

    >>> import sympy
    >>> from sympy import Point3D
    >>> from sympy.geometry import Line3D, Segment3D
    >>> L = Line3D(Point3D(2, 3, 4), Point3D(3, 5, 1))
    >>> L
    Line3D(Point3D(2, 3, 4), Point3D(3, 5, 1))
    >>> L.points
    (Point3D(2, 3, 4), Point3D(3, 5, 1))
    """

    def __new__(cls, p1, pt=None, direction_ratio=[], **kwargs):
        if isinstance(p1, LinearEntity3D):
            if pt is not None:
                raise ValueError('if p1 is a LinearEntity, pt must be None.')
            p1, pt = p1.args
        else:
            p1 = Point(p1, dim=3)
        if pt is not None and len(direction_ratio) == 0:
            pt = Point(pt, dim=3)
        elif len(direction_ratio) == 3 and pt is None:
            pt = Point3D(p1.x + direction_ratio[0], p1.y + direction_ratio[1],
                         p1.z + direction_ratio[2])
        else:
            raise ValueError('A 2nd Point or keyword "direction_ratio" must '
            'be used.')

        return LinearEntity3D.__new__(cls, p1, pt, **kwargs)

    def equation(self, x='x', y='y', z='z', k='k'):
        """The equation of the line in 3D

        Parameters
        ==========

        x : str, optional
            The name to use for the x-axis, default value is 'x'.
        y : str, optional
            The name to use for the y-axis, default value is 'y'.
        z : str, optional
            The name to use for the x-axis, default value is 'z'.

        Returns
        =======

        equation : tuple

        Examples
        ========

        >>> from sympy import Point3D, Line3D
        >>> p1, p2 = Point3D(1, 0, 0), Point3D(5, 3, 0)
        >>> l1 = Line3D(p1, p2)
        >>> l1.equation()
        (x/4 - 1/4, y/3, zoo*z, k)

        """
        x, y, z, k = _symbol(x), _symbol(y), _symbol(z), _symbol(k)
        p1, p2 = self.points
        a = p1.direction_ratio(p2)
        return (((x - p1.x)/a[0]), ((y - p1.y)/a[1]),
                ((z - p1.z)/a[2]), k)

class Ray3D(LinearEntity3D, Ray):
    """
    A Ray is a semi-line in the space with a source point and a direction.

    Parameters
    ==========

    p1 : Point3D
        The source of the Ray
    p2 : Point or a direction vector
    direction_ratio: Determines the direction in which the Ray propagates.


    Attributes
    ==========

    source
    xdirection
    ydirection
    zdirection

    See Also
    ========

    sympy.geometry.point.Point3D, Line3D


    Examples
    ========

    >>> import sympy
    >>> from sympy import Point3D, pi
    >>> from sympy.geometry import Ray3D
    >>> r = Ray3D(Point3D(2, 3, 4), Point3D(3, 5, 0))
    >>> r
    Ray3D(Point3D(2, 3, 4), Point3D(3, 5, 0))
    >>> r.points
    (Point3D(2, 3, 4), Point3D(3, 5, 0))
    >>> r.source
    Point3D(2, 3, 4)
    >>> r.xdirection
    oo
    >>> r.ydirection
    oo
    >>> r.direction_ratio
    [1, 2, -4]

    """

    def __new__(cls, p1, pt=None, direction_ratio=[], **kwargs):
        if isinstance(p1, LinearEntity3D):
            if pt is not None:
                raise ValueError('If p1 is a LinearEntity, pt must be None')
            p1, pt = p1.args
        else:
            p1 = Point(p1, dim=3)
        if pt is not None and len(direction_ratio) == 0:
            pt = Point(pt, dim=3)
        elif len(direction_ratio) == 3 and pt is None:
            pt = Point3D(p1.x + direction_ratio[0], p1.y + direction_ratio[1],
                         p1.z + direction_ratio[2])
        else:
            raise ValueError('A 2nd Point or keyword "direction_ratio" must'
            'be used.')

        return LinearEntity3D.__new__(cls, p1, pt, **kwargs)

    @property
    def xdirection(self):
        """The x direction of the ray.

        Positive infinity if the ray points in the positive x direction,
        negative infinity if the ray points in the negative x direction,
        or 0 if the ray is vertical.

        See Also
        ========

        ydirection

        Examples
        ========

        >>> from sympy import Point3D, Ray3D
        >>> p1, p2, p3 = Point3D(0, 0, 0), Point3D(1, 1, 1), Point3D(0, -1, 0)
        >>> r1, r2 = Ray3D(p1, p2), Ray3D(p1, p3)
        >>> r1.xdirection
        oo
        >>> r2.xdirection
        0

        """
        if self.p1.x < self.p2.x:
            return S.Infinity
        elif self.p1.x == self.p2.x:
            return S.Zero
        else:
            return S.NegativeInfinity

    @property
    def ydirection(self):
        """The y direction of the ray.

        Positive infinity if the ray points in the positive y direction,
        negative infinity if the ray points in the negative y direction,
        or 0 if the ray is horizontal.

        See Also
        ========

        xdirection

        Examples
        ========

        >>> from sympy import Point3D, Ray3D
        >>> p1, p2, p3 = Point3D(0, 0, 0), Point3D(-1, -1, -1), Point3D(-1, 0, 0)
        >>> r1, r2 = Ray3D(p1, p2), Ray3D(p1, p3)
        >>> r1.ydirection
        -oo
        >>> r2.ydirection
        0

        """
        if self.p1.y < self.p2.y:
            return S.Infinity
        elif self.p1.y == self.p2.y:
            return S.Zero
        else:
            return S.NegativeInfinity

    @property
    def zdirection(self):
        """The z direction of the ray.

        Positive infinity if the ray points in the positive z direction,
        negative infinity if the ray points in the negative z direction,
        or 0 if the ray is horizontal.

        See Also
        ========

        xdirection

        Examples
        ========

        >>> from sympy import Point3D, Ray3D
        >>> p1, p2, p3 = Point3D(0, 0, 0), Point3D(-1, -1, -1), Point3D(-1, 0, 0)
        >>> r1, r2 = Ray3D(p1, p2), Ray3D(p1, p3)
        >>> r1.ydirection
        -oo
        >>> r2.ydirection
        0
        >>> r2.zdirection
        0

        """
        if self.p1.z < self.p2.z:
            return S.Infinity
        elif self.p1.z == self.p2.z:
            return S.Zero
        else:
            return S.NegativeInfinity

class Segment3D(LinearEntity3D, Segment):
    """A undirected line segment in a 3D space.

    Parameters
    ==========

    p1 : Point3D
    p2 : Point3D

    Attributes
    ==========

    length : number or sympy expression
    midpoint : Point3D

    See Also
    ========

    sympy.geometry.point.Point3D, Line3D

    Examples
    ========

    >>> import sympy
    >>> from sympy import Point3D
    >>> from sympy.geometry import Segment3D
    >>> Segment3D((1, 0, 0), (1, 1, 1)) # tuples are interpreted as pts
    Segment3D(Point3D(1, 0, 0), Point3D(1, 1, 1))
    >>> s = Segment3D(Point3D(4, 3, 9), Point3D(1, 1, 7))
    >>> s
    Segment3D(Point3D(1, 1, 7), Point3D(4, 3, 9))
    >>> s.points
    (Point3D(1, 1, 7), Point3D(4, 3, 9))
    >>> s.length
    sqrt(17)
    >>> s.midpoint
    Point3D(5/2, 2, 8)

    """

    def __new__(cls, p1, p2, **kwargs):
        # Reorder the two points under the following ordering:
        #   if p1.x != p2.x then p1.x < p2.x
        #   if p1.x == p2.x then p1.y < p2.y
        #   The z-coordinate will not come into picture while ordering
        p1 = Point(p1, dim=3)
        p2 = Point(p2, dim=3)

        if p1 == p2:
            return p1
        if (p1.x > p2.x) == True:
            p1, p2 = p2, p1
        elif (p1.x == p2.x) == True and (p1.y > p2.y) == True:
            p1, p2 = p2, p1
        return LinearEntity3D.__new__(cls, p1, p2, **kwargs)
