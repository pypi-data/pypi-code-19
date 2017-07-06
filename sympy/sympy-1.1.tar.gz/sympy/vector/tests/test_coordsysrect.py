from sympy.utilities.exceptions import SymPyDeprecationWarning
import warnings
from sympy.vector.coordsysrect import CoordSys3D, CoordSysCartesian
from sympy.vector.scalar import BaseScalar
from sympy import sin, cos, sqrt, pi, ImmutableMatrix as Matrix, \
     symbols, simplify, zeros, expand
from sympy.vector.functions import express
from sympy.vector.point import Point
from sympy.vector.vector import Vector
from sympy.vector.orienters import (AxisOrienter, BodyOrienter,
                                    SpaceOrienter, QuaternionOrienter)

a, b, c, q = symbols('a b c q')
q1, q2, q3, q4 = symbols('q1 q2 q3 q4')


def test_func_args():
    A = CoordSys3D('A')
    assert A.x.func(*A.x.args) == A.x
    expr = 3*A.x + 4*A.y
    assert expr.func(*expr.args) == expr
    assert A.i.func(*A.i.args) == A.i
    v = A.x*A.i + A.y*A.j + A.z*A.k
    assert v.func(*v.args) == v
    assert A.origin.func(*A.origin.args) == A.origin


def test_coordsyscartesian_equivalence():
    A = CoordSys3D('A')
    A1 = CoordSys3D('A')
    assert A1 == A
    B = CoordSys3D('B')
    assert A != B


def test_orienters():
    A = CoordSys3D('A')
    axis_orienter = AxisOrienter(a, A.k)
    body_orienter = BodyOrienter(a, b, c, '123')
    space_orienter = SpaceOrienter(a, b, c, '123')
    q_orienter = QuaternionOrienter(q1, q2, q3, q4)
    assert axis_orienter.rotation_matrix(A) == Matrix([
        [ cos(a), sin(a), 0],
        [-sin(a), cos(a), 0],
        [      0,      0, 1]])
    assert body_orienter.rotation_matrix() == Matrix([
        [ cos(b)*cos(c),  sin(a)*sin(b)*cos(c) + sin(c)*cos(a),
          sin(a)*sin(c) - sin(b)*cos(a)*cos(c)],
        [-sin(c)*cos(b), -sin(a)*sin(b)*sin(c) + cos(a)*cos(c),
         sin(a)*cos(c) + sin(b)*sin(c)*cos(a)],
        [        sin(b),                        -sin(a)*cos(b),
                 cos(a)*cos(b)]])
    assert space_orienter.rotation_matrix() == Matrix([
        [cos(b)*cos(c), sin(c)*cos(b),       -sin(b)],
        [sin(a)*sin(b)*cos(c) - sin(c)*cos(a),
         sin(a)*sin(b)*sin(c) + cos(a)*cos(c), sin(a)*cos(b)],
        [sin(a)*sin(c) + sin(b)*cos(a)*cos(c), -sin(a)*cos(c) +
         sin(b)*sin(c)*cos(a), cos(a)*cos(b)]])
    assert q_orienter.rotation_matrix() == Matrix([
        [q1**2 + q2**2 - q3**2 - q4**2, 2*q1*q4 + 2*q2*q3,
         -2*q1*q3 + 2*q2*q4],
        [-2*q1*q4 + 2*q2*q3, q1**2 - q2**2 + q3**2 - q4**2,
         2*q1*q2 + 2*q3*q4],
        [2*q1*q3 + 2*q2*q4,
         -2*q1*q2 + 2*q3*q4, q1**2 - q2**2 - q3**2 + q4**2]])


def test_coordinate_vars():
    """
    Tests the coordinate variables functionality with respect to
    reorientation of coordinate systems.
    """
    A = CoordSys3D('A')
    # Note that the name given on the lhs is different from A.x._name
    assert BaseScalar('A.x', 0, A, 'A_x', r'\mathbf{{x}_{A}}') == A.x
    assert BaseScalar('A.y', 1, A, 'A_y', r'\mathbf{{y}_{A}}') == A.y
    assert BaseScalar('A.z', 2, A, 'A_z', r'\mathbf{{z}_{A}}') == A.z
    assert BaseScalar('A.x', 0, A, 'A_x', r'\mathbf{{x}_{A}}').__hash__() == A.x.__hash__()
    assert isinstance(A.x, BaseScalar) and \
           isinstance(A.y, BaseScalar) and \
           isinstance(A.z, BaseScalar)
    assert A.x*A.y == A.y*A.x
    assert A.scalar_map(A) == {A.x: A.x, A.y: A.y, A.z: A.z}
    assert A.x.system == A
    assert A.x.diff(A.x) == 1
    B = A.orient_new_axis('B', q, A.k)
    assert B.scalar_map(A) == {B.z: A.z, B.y: -A.x*sin(q) + A.y*cos(q),
                                 B.x: A.x*cos(q) + A.y*sin(q)}
    assert A.scalar_map(B) == {A.x: B.x*cos(q) - B.y*sin(q),
                                 A.y: B.x*sin(q) + B.y*cos(q), A.z: B.z}
    assert express(B.x, A, variables=True) == A.x*cos(q) + A.y*sin(q)
    assert express(B.y, A, variables=True) == -A.x*sin(q) + A.y*cos(q)
    assert express(B.z, A, variables=True) == A.z
    assert expand(express(B.x*B.y*B.z, A, variables=True)) == \
           expand(A.z*(-A.x*sin(q) + A.y*cos(q))*(A.x*cos(q) + A.y*sin(q)))
    assert express(B.x*B.i + B.y*B.j + B.z*B.k, A) == \
           (B.x*cos(q) - B.y*sin(q))*A.i + (B.x*sin(q) + \
           B.y*cos(q))*A.j + B.z*A.k
    assert simplify(express(B.x*B.i + B.y*B.j + B.z*B.k, A, \
                            variables=True)) == \
           A.x*A.i + A.y*A.j + A.z*A.k
    assert express(A.x*A.i + A.y*A.j + A.z*A.k, B) == \
           (A.x*cos(q) + A.y*sin(q))*B.i + \
           (-A.x*sin(q) + A.y*cos(q))*B.j + A.z*B.k
    assert simplify(express(A.x*A.i + A.y*A.j + A.z*A.k, B, \
                            variables=True)) == \
           B.x*B.i + B.y*B.j + B.z*B.k
    N = B.orient_new_axis('N', -q, B.k)
    assert N.scalar_map(A) == \
           {N.x: A.x, N.z: A.z, N.y: A.y}
    C = A.orient_new_axis('C', q, A.i + A.j + A.k)
    mapping = A.scalar_map(C)
    assert mapping[A.x].equals(C.x*(2*cos(q) + 1)/3 +
                            C.y*(-2*sin(q + pi/6) + 1)/3 +
                            C.z*(-2*cos(q + pi/3) + 1)/3)
    assert mapping[A.y].equals(C.x*(-2*cos(q + pi/3) + 1)/3 +
                            C.y*(2*cos(q) + 1)/3 +
                            C.z*(-2*sin(q + pi/6) + 1)/3)
    assert mapping[A.z].equals(C.x*(-2*sin(q + pi/6) + 1)/3 +
                            C.y*(-2*cos(q + pi/3) + 1)/3 +
                            C.z*(2*cos(q) + 1)/3)
    D = A.locate_new('D', a*A.i + b*A.j + c*A.k)
    assert D.scalar_map(A) == {D.z: A.z - c, D.x: A.x - a, D.y: A.y - b}
    E = A.orient_new_axis('E', a, A.k, a*A.i + b*A.j + c*A.k)
    assert A.scalar_map(E) == {A.z: E.z + c,
                               A.x: E.x*cos(a) - E.y*sin(a) + a,
                               A.y: E.x*sin(a) + E.y*cos(a) + b}
    assert E.scalar_map(A) == {E.x: (A.x - a)*cos(a) + (A.y - b)*sin(a),
                               E.y: (-A.x + a)*sin(a) + (A.y - b)*cos(a),
                               E.z: A.z - c}
    F = A.locate_new('F', Vector.zero)
    assert A.scalar_map(F) == {A.z: F.z, A.x: F.x, A.y: F.y}


def test_rotation_matrix():
    N = CoordSys3D('N')
    A = N.orient_new_axis('A', q1, N.k)
    B = A.orient_new_axis('B', q2, A.i)
    C = B.orient_new_axis('C', q3, B.j)
    D = N.orient_new_axis('D', q4, N.j)
    E = N.orient_new_space('E', q1, q2, q3, '123')
    F = N.orient_new_quaternion('F', q1, q2, q3, q4)
    G = N.orient_new_body('G', q1, q2, q3, '123')
    assert N.rotation_matrix(C) == Matrix([
        [- sin(q1) * sin(q2) * sin(q3) + cos(q1) * cos(q3), - sin(q1) *
        cos(q2), sin(q1) * sin(q2) * cos(q3) + sin(q3) * cos(q1)], \
        [sin(q1) * cos(q3) + sin(q2) * sin(q3) * cos(q1), \
         cos(q1) * cos(q2), sin(q1) * sin(q3) - sin(q2) * cos(q1) * \
         cos(q3)], [- sin(q3) * cos(q2), sin(q2), cos(q2) * cos(q3)]])
    test_mat = D.rotation_matrix(C) - Matrix(
        [[cos(q1) * cos(q3) * cos(q4) - sin(q3) * (- sin(q4) * cos(q2) +
        sin(q1) * sin(q2) * cos(q4)), - sin(q2) * sin(q4) - sin(q1) *
            cos(q2) * cos(q4), sin(q3) * cos(q1) * cos(q4) + cos(q3) * \
          (- sin(q4) * cos(q2) + sin(q1) * sin(q2) * cos(q4))], \
         [sin(q1) * cos(q3) + sin(q2) * sin(q3) * cos(q1), cos(q1) * \
          cos(q2), sin(q1) * sin(q3) - sin(q2) * cos(q1) * cos(q3)], \
         [sin(q4) * cos(q1) * cos(q3) - sin(q3) * (cos(q2) * cos(q4) + \
                                                   sin(q1) * sin(q2) * \
                                                   sin(q4)), sin(q2) *
                cos(q4) - sin(q1) * sin(q4) * cos(q2), sin(q3) * \
          sin(q4) * cos(q1) + cos(q3) * (cos(q2) * cos(q4) + \
                                         sin(q1) * sin(q2) * sin(q4))]])
    assert test_mat.expand() == zeros(3, 3)
    assert E.rotation_matrix(N) == Matrix(
        [[cos(q2)*cos(q3), sin(q3)*cos(q2), -sin(q2)],
        [sin(q1)*sin(q2)*cos(q3) - sin(q3)*cos(q1), \
         sin(q1)*sin(q2)*sin(q3) + cos(q1)*cos(q3), sin(q1)*cos(q2)], \
         [sin(q1)*sin(q3) + sin(q2)*cos(q1)*cos(q3), - \
          sin(q1)*cos(q3) + sin(q2)*sin(q3)*cos(q1), cos(q1)*cos(q2)]])
    assert F.rotation_matrix(N) == Matrix([[
        q1**2 + q2**2 - q3**2 - q4**2,
        2*q1*q4 + 2*q2*q3, -2*q1*q3 + 2*q2*q4],[ -2*q1*q4 + 2*q2*q3,
            q1**2 - q2**2 + q3**2 - q4**2, 2*q1*q2 + 2*q3*q4],
                                           [2*q1*q3 + 2*q2*q4,
                                            -2*q1*q2 + 2*q3*q4,
                                q1**2 - q2**2 - q3**2 + q4**2]])
    assert G.rotation_matrix(N) == Matrix([[
        cos(q2)*cos(q3),  sin(q1)*sin(q2)*cos(q3) + sin(q3)*cos(q1),
        sin(q1)*sin(q3) - sin(q2)*cos(q1)*cos(q3)], [
            -sin(q3)*cos(q2), -sin(q1)*sin(q2)*sin(q3) + cos(q1)*cos(q3),
            sin(q1)*cos(q3) + sin(q2)*sin(q3)*cos(q1)],[
                sin(q2), -sin(q1)*cos(q2), cos(q1)*cos(q2)]])


def test_vector():
    """
    Tests the effects of orientation of coordinate systems on
    basic vector operations.
    """
    N = CoordSys3D('N')
    A = N.orient_new_axis('A', q1, N.k)
    B = A.orient_new_axis('B', q2, A.i)
    C = B.orient_new_axis('C', q3, B.j)

    #Test to_matrix
    v1 = a*N.i + b*N.j + c*N.k
    assert v1.to_matrix(A) == Matrix([[ a*cos(q1) + b*sin(q1)],
                                      [-a*sin(q1) + b*cos(q1)],
                                      [                     c]])

    #Test dot
    assert N.i.dot(A.i) == cos(q1)
    assert N.i.dot(A.j) == -sin(q1)
    assert N.i.dot(A.k) == 0
    assert N.j.dot(A.i) == sin(q1)
    assert N.j.dot(A.j) == cos(q1)
    assert N.j.dot(A.k) == 0
    assert N.k.dot(A.i) == 0
    assert N.k.dot(A.j) == 0
    assert N.k.dot(A.k) == 1

    assert N.i.dot(A.i + A.j) == -sin(q1) + cos(q1) == \
           (A.i + A.j).dot(N.i)

    assert A.i.dot(C.i) == cos(q3)
    assert A.i.dot(C.j) == 0
    assert A.i.dot(C.k) == sin(q3)
    assert A.j.dot(C.i) == sin(q2)*sin(q3)
    assert A.j.dot(C.j) == cos(q2)
    assert A.j.dot(C.k) == -sin(q2)*cos(q3)
    assert A.k.dot(C.i) == -cos(q2)*sin(q3)
    assert A.k.dot(C.j) == sin(q2)
    assert A.k.dot(C.k) == cos(q2)*cos(q3)

    #Test cross
    assert N.i.cross(A.i) == sin(q1)*A.k
    assert N.i.cross(A.j) == cos(q1)*A.k
    assert N.i.cross(A.k) == -sin(q1)*A.i - cos(q1)*A.j
    assert N.j.cross(A.i) == -cos(q1)*A.k
    assert N.j.cross(A.j) == sin(q1)*A.k
    assert N.j.cross(A.k) == cos(q1)*A.i - sin(q1)*A.j
    assert N.k.cross(A.i) == A.j
    assert N.k.cross(A.j) == -A.i
    assert N.k.cross(A.k) == Vector.zero

    assert N.i.cross(A.i) == sin(q1)*A.k
    assert N.i.cross(A.j) == cos(q1)*A.k
    assert N.i.cross(A.i + A.j) == sin(q1)*A.k + cos(q1)*A.k
    assert (A.i + A.j).cross(N.i) == (-sin(q1) - cos(q1))*N.k

    assert A.i.cross(C.i) == sin(q3)*C.j
    assert A.i.cross(C.j) == -sin(q3)*C.i + cos(q3)*C.k
    assert A.i.cross(C.k) == -cos(q3)*C.j
    assert C.i.cross(A.i) == (-sin(q3)*cos(q2))*A.j + \
           (-sin(q2)*sin(q3))*A.k
    assert C.j.cross(A.i) == (sin(q2))*A.j + (-cos(q2))*A.k
    assert express(C.k.cross(A.i), C).trigsimp() == cos(q3)*C.j

def test_orient_new_methods():
    N = CoordSys3D('N')
    orienter1 = AxisOrienter(q4, N.j)
    orienter2 = SpaceOrienter(q1, q2, q3, '123')
    orienter3 = QuaternionOrienter(q1, q2, q3, q4)
    orienter4 = BodyOrienter(q1, q2, q3, '123')
    D = N.orient_new('D', (orienter1, ))
    E = N.orient_new('E', (orienter2, ))
    F = N.orient_new('F', (orienter3, ))
    G = N.orient_new('G', (orienter4, ))
    assert D == N.orient_new_axis('D', q4, N.j)
    assert E == N.orient_new_space('E', q1, q2, q3, '123')
    assert F == N.orient_new_quaternion('F', q1, q2, q3, q4)
    assert G == N.orient_new_body('G', q1, q2, q3, '123')


def test_locatenew_point():
    """
    Tests Point class, and locate_new method in CoordSysCartesian.
    """
    A = CoordSys3D('A')
    assert isinstance(A.origin, Point)
    v = a*A.i + b*A.j + c*A.k
    C = A.locate_new('C', v)
    assert C.origin.position_wrt(A) == \
           C.position_wrt(A) == \
           C.origin.position_wrt(A.origin) == v
    assert A.origin.position_wrt(C) == \
           A.position_wrt(C) == \
           A.origin.position_wrt(C.origin) == -v
    assert A.origin.express_coordinates(C) == (-a, -b, -c)
    p = A.origin.locate_new('p', -v)
    assert p.express_coordinates(A) == (-a, -b, -c)
    assert p.position_wrt(C.origin) == p.position_wrt(C) == \
           -2 * v
    p1 = p.locate_new('p1', 2*v)
    assert p1.position_wrt(C.origin) == Vector.zero
    assert p1.express_coordinates(C) == (0, 0, 0)
    p2 = p.locate_new('p2', A.i)
    assert p1.position_wrt(p2) == 2*v - A.i
    assert p2.express_coordinates(C) == (-2*a + 1, -2*b, -2*c)


def test_evalf():
    A = CoordSys3D('A')
    v = 3*A.i + 4*A.j + a*A.k
    assert v.n() == v.evalf()
    assert v.evalf(subs={a:1}) == v.subs(a, 1).evalf()


def test_lame_coefficients():
    a = CoordSys3D('a')
    a._set_lame_coefficient_mapping('spherical')
    assert a.lame_coefficients() == (1, a.x, sin(a.y)*a.x)
    a = CoordSys3D('a')
    assert a.lame_coefficients() == (1, 1, 1)
    a = CoordSys3D('a')
    a._set_lame_coefficient_mapping('cartesian')
    assert a.lame_coefficients() == (1, 1, 1)
    a = CoordSys3D('a')
    a._set_lame_coefficient_mapping('cylindrical')
    assert a.lame_coefficients() == (1, a.y, 1)


def test_transformation_equations():
    from sympy import symbols
    x, y, z = symbols('x y z')
    a = CoordSys3D('a')
    # Str
    a._connect_to_standard_cartesian('spherical')
    assert a._transformation_equations() == (a.x * sin(a.y) * cos(a.z),
                          a.x * sin(a.y) * sin(a.z),
                          a.x * cos(a.y))
    assert a.lame_coefficients() == (1, a.x, a.x * sin(a.y))
    a._connect_to_standard_cartesian('cylindrical')
    assert a._transformation_equations() == (a.x * cos(a.y), a.x * sin(a.y), a.z)
    assert a.lame_coefficients() == (1, a.y, 1)
    a._connect_to_standard_cartesian('cartesian')
    assert a._transformation_equations() == (a.x, a.y, a.z)
    assert a.lame_coefficients() == (1, 1, 1)
    # Variables and expressions
    a._connect_to_standard_cartesian(((x, y, z), (x, y, z)))
    assert a._transformation_equations() == (a.x, a.y, a.z)
    assert a.lame_coefficients() == (1, 1, 1)
    a._connect_to_standard_cartesian(((x, y, z), ((x * cos(y), x * sin(y), z))))
    assert a._transformation_equations() == (a.x * cos(a.y), a.x * sin(a.y), a.z)
    assert simplify(a.lame_coefficients()) == (1, sqrt(a.x**2), 1)
    a._connect_to_standard_cartesian(((x, y, z), (x * sin(y) * cos(z), x * sin(y) * sin(z), x * cos(y))))
    assert a._transformation_equations() == (a.x * sin(a.y) * cos(a.z),
                          a.x * sin(a.y) * sin(a.z),
                          a.x * cos(a.y))
    assert simplify(a.lame_coefficients()) == (1, sqrt(a.x**2), sqrt(sin(a.y)**2*a.x**2))
    # Equations
    a._connect_to_standard_cartesian((a.x*sin(a.y)*cos(a.z), a.x*sin(a.y)*sin(a.z), a.x*cos(a.y)))
    assert a._transformation_equations() == (a.x * sin(a.y) * cos(a.z),
                          a.x * sin(a.y) * sin(a.z),
                          a.x * cos(a.y))
    assert simplify(a.lame_coefficients()) == (1, sqrt(a.x**2), sqrt(sin(a.y)**2*a.x**2))
    a._connect_to_standard_cartesian((a.x, a.y, a.z))
    assert a._transformation_equations() == (a.x, a.y, a.z)
    assert simplify(a.lame_coefficients()) == (1, 1, 1)
    a._connect_to_standard_cartesian((a.x * cos(a.y), a.x * sin(a.y), a.z))
    assert a._transformation_equations() == (a.x * cos(a.y), a.x * sin(a.y), a.z)
    assert simplify(a.lame_coefficients()) == (1, sqrt(a.x**2), 1)


def test_coordsys3d():
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=SymPyDeprecationWarning)
        assert CoordSysCartesian("C") == CoordSys3D("C")
