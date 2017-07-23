from mvpoly.cube import MVPolyCube
import numpy as np
import unittest

class TestMVPolyCube(unittest.TestCase) :

    def test_construct_from_empty(self) :
        obtained = MVPolyCube().coef
        expected = []
        self.assertTrue((expected == obtained).all(),
                        "bad constructor:\n{0!s}".format(repr(obtained)))


class TestMVPolyCubeDtype(unittest.TestCase) :

    def setUp(self) :
        a = [1, 2, 3, 4]
        self.f = MVPolyCube(a, dtype=float)
        self.i = MVPolyCube(a, dtype=int)

    def test_construct_get_dtype(self) :
        self.assertTrue(self.f.dtype == float,
                        "bad dtype: {0!s}".format(repr(self.f.dtype)))
        self.assertTrue(self.i.dtype == int,
                        "bad dtype: {0!s}".format(repr(self.i.dtype)))

    def test_construct_set_dtype(self) :
        self.f.dtype = bool
        self.assertTrue(self.f.dtype == bool,
                        "bad dtype: {0!s}".format(repr(self.f.dtype)))

    def test_construct_dtype_persist(self) :
        p = MVPolyCube([1, 2], dtype=int)
        qs = [p+p, p+1, 1+p, p*p, 2*p, p*2, p**3, 2*p]
        for q in qs :
            self.assertTrue(q.dtype == int,
                            "bad dtype: {0!s}".format(repr(q.dtype)))


class TestMVPolyCubeSetitem(unittest.TestCase) :

    def test_regression_broadcast(self) :
        # regression in __setitem__() : when passed an empty
        # tuple the value was broadcast to the whole array,
        # we don't want that
        coef = np.zeros((3,3), dtype=int)
        p = MVPolyCube(coef, dtype=int)
        p[()] = 1
        q = MVPolyCube.one(dtype=int)
        self.assertTrue(p == q, "setitem broadcast regression")


class TestMVPolyCubeEqual(unittest.TestCase) :

    def test_equal_self(self) :
        p = MVPolyCube([[1, 2, 3], [4, 5, 6]])
        self.assertTrue(p == p, "bad equality")

    def test_equal_diffsize(self) :
        p = MVPolyCube([[1, 2, 0],
                        [4, 5, 0]])
        q = MVPolyCube([[1, 2],
                        [4, 5]])
        self.assertTrue(p == q, "bad equality")

    def test_equal_diffdim(self) :
        p = MVPolyCube([[1, 2, 3],
                        [0, 0, 0]])
        q = MVPolyCube([1, 2, 3])
        self.assertTrue(p == q, "bad equality")

    def test_unequal(self) :
        p = MVPolyCube([1, 2, 3])
        q = MVPolyCube([1, 2, 3, 4])
        self.assertFalse(p == q, "bad equality")
        self.assertTrue(p != q, "bad non-equality")


class TestMVPolyCubeNonzero(unittest.TestCase) :

    def test_nonzero_zero(self):
        p = MVPolyCube.zero()
        self.assertTrue(p.nonzero == [])

    def test_nonzero_one(self):
        p = MVPolyCube.one()
        self.assertTrue(p.nonzero == [((0,), 1)])

    def test_nonzero_enumerate(self) :
        x, y = MVPolyCube.variables(2)
        p = 3*x + y**2 + 7
        obt = p.nonzero
        exp = [((0, 0), 7.0), ((1, 0), 3.0), ((0, 2), 1.0)]
        self.assertTrue(sorted(obt) == sorted(exp))


class TestMVPolyCubeAdd(unittest.TestCase) :

    def setUp(self) :
        self.A = MVPolyCube([1, 2, 3])
        self.B = MVPolyCube([[1], [1]])

    def test_add1(self) :
        obtained = (self.A + self.B).coef
        expected = [[2, 2, 3],
                    [1, 0, 0]]
        self.assertTrue((expected == obtained).all(),
                        "bad sum:\n{0!s}".format(repr(obtained)))

    def test_add2(self) :
        obtained = (self.A + 1).coef
        expected = [2, 2, 3]
        self.assertTrue((expected == obtained).all(),
                        "bad sum:\n{0!s}".format(repr(obtained)))

    def test_add3(self) :
        obtained = (1 + self.A).coef
        expected = [2, 2, 3]
        self.assertTrue((expected == obtained).all(),
                        "bad sum:\n{0!s}".format(repr(obtained)))


class TestMVPolyCubeMultiply(unittest.TestCase) :

    def setUp(self) :
        self.A = MVPolyCube([1, 1], dtype=int)
        self.B = MVPolyCube([[1, 1], [1, 1]], dtype=int)

    def test_multiply_scalar(self) :
        obtained = (2 * self.A).coef
        expected = [2, 2]
        self.assertTrue((expected == obtained).all(),
                        "bad multiply:\n{0!s}".format(repr(obtained)))

    def test_multiply_1d(self) :
        obtained = (self.A * self.A).coef
        expected = [1, 2, 1]
        self.assertTrue((expected == obtained).all(),
                        "bad multiply:\n{0!s}".format(repr(obtained)))

    def test_multiply_dtype(self) :
        self.A.dtype = int
        C = self.A * self.A
        self.assertTrue((C.dtype == int),
                        "bad product type:\n{0!s}".format(repr(C.dtype)))

    def test_multiply_dimension(self) :
        expected = [[1, 1],
                    [2, 2],
                    [1, 1]]
        obtained = (self.A * self.B).coef
        self.assertTrue((expected == obtained).all(),
                        "bad AB multiply:\n{0!s}".format(repr(obtained)))
        obtained = (self.B * self.A).coef
        self.assertTrue((expected == obtained).all(),
                        "bad BA multiply:\n{0!s}".format(repr(obtained)))

    def test_multiply_arithmetic(self) :
        x, y = MVPolyCube.variables(2, dtype=int)
        p1 = (x + y)*(2*x - y)
        p2 = 2*x**2 + x*y - y**2
        self.assertTrue((p1.coef == p2.coef).all(),
                        "bad multiply:\n{0!s}\n{1!s}".format(repr(p1.coef),
                                                   repr(p2.coef)))

    def test_multiply_complex(self) :
        x, y = MVPolyCube.variables(2, dtype=complex)
        p1 = (x + y)*(x + 1j*y)
        p2 = x**2 + (1 + 1j)*x*y + 1j*y**2
        self.assertTrue((p1.coef == p2.coef).all(),
                        "bad multiply:\n{0!s}\n{1!s}".format(repr(p1.coef),
                                                   repr(p2.coef)))


class TestMVPolyCubePower(unittest.TestCase) :

    def test_power_small(self) :
        A = MVPolyCube([1, 1])
        obtained = (A**2).coef
        expected = [1, 2, 1]
        self.assertTrue((expected == obtained).all(),
                        "bad power:\n{0!s}".format(repr(obtained)))
        obtained = (A**3).coef
        expected = [1, 3, 3, 1]
        self.assertTrue((expected == obtained).all(),
                        "bad power:\n{0!s}".format(repr(obtained)))

    def test_power_types(self) :
        A = MVPolyCube([1, 1], dtype=int)
        obtained = (A**5).coef
        expected = [1, 5, 10, 10, 5, 1]
        self.assertTrue((expected == obtained).all(),
                        "bad power:\n{0!s}".format(repr(obtained)))
        self.assertTrue(obtained.dtype == int,
                        "wrong data type for power: {0!s}".format(repr(obtained.dtype)))

    def test_power_badargs(self) :
        A = MVPolyCube([1, 1])
        with self.assertRaises(TypeError) :
            A**1.5
        with self.assertRaises(ArithmeticError) :
            A**-2


class TestMVPolyCubeMonomials(unittest.TestCase) :

    def test_monomials_constant(self) :
        L = MVPolyCube.monomials(2, 0)
        self.assertTrue(len(L) == 1)
        self.assertTrue(L[0].coef == [[1]],
                        "{0!s}".format(repr(L[0].coef)))

    def test_monomials_linear(self) :
        L = MVPolyCube.monomials(2, 1)
        self.assertTrue(len(L) == 3)
        self.assertTrue((L[0].coef == [[1]]).all(),
                        "{0!s}".format(repr(L[0].coef)))
        self.assertTrue((L[1].coef == [[0, 0],
                                       [1, 0]]).all(),
                        "{0!s}".format(repr(L[1].coef)))
        self.assertTrue((L[2].coef == [[0, 1],
                                       [0, 0]]).all(),
                        "{0!s}".format(repr(L[2].coef)))

    def test_monomials_quadratic(self) :
        L = MVPolyCube.monomials(2, 2)
        self.assertTrue(len(L) == 6)
        self.assertTrue((L[0].coef == [[1]]).all(),
                        "{0!s}".format(repr(L[0].coef)))
        self.assertTrue((L[1].coef == [[0, 0],
                                       [1, 0]]).all(),
                        "{0!s}".format(repr(L[1].coef)))
        self.assertTrue((L[2].coef == [[0, 1],
                                       [0, 0]]).all(),
                        "{0!s}".format(repr(L[2].coef)))
        self.assertTrue((L[3].coef == [[0, 0, 0],
                                       [0, 0, 0],
                                       [1, 0, 0]]).all(),
                        "{0!s}".format(repr(L[3].coef)))
        self.assertTrue((L[4].coef == [[0, 0, 0],
                                       [0, 1, 0],
                                       [0, 0, 0]]).all(),
                        "{0!s}".format(repr(L[4].coef)))
        self.assertTrue((L[5].coef == [[0, 0, 1],
                                       [0, 0, 0],
                                       [0, 0, 0]]).all(),
                        "{0!s}".format(repr(L[5].coef)))


class TestMVPolyCubeVariables(unittest.TestCase) :

    def test_variables_count(self) :
        for n in [2,3,4] :
            M = MVPolyCube.variables(n)
            self.assertTrue(len(M) == n)

    def test_variables_create(self) :
        x, y, z = MVPolyCube.variables(3)
        self.assertTrue((x.coef == [[[0]],[[1]]]).all(),
                        "bad x variable: \n{0!s}".format(repr(x.coef)))
        self.assertTrue((y.coef == [[[0],[1]]]).all(),
                        "bad y variable: \n{0!s}".format(repr(y.coef)))
        self.assertTrue((z.coef == [[[0, 1]]]).all(),
                        "bad z variable: \n{0!s}".format(repr(z.coef)))

    def test_variables_build(self) :
        x, y = MVPolyCube.variables(2)
        p = 2*x**2 + 3*x*y + 1
        self.assertTrue((p.coef == [[1, 0], [0, 3], [2, 0]]).all(),
                        "bad build: \n{0!s}".format(repr(p.coef)))

    def test_variables_dtype(self) :
        x, y = MVPolyCube.variables(2, dtype=int)
        p = 2*x**2 + 3*x*y + 1
        for m in (x, y, p) :
            self.assertTrue(m.dtype == int,
                            "bad type: \n{0!s}".format(repr(m.dtype)))
            self.assertTrue(m.coef.dtype == int,
                            "bad type: \n{0!s}".format(repr(m.coef.dtype)))


class TestMVPolyCubeNeg(unittest.TestCase) :

    def test_negation(self) :
        x, y = MVPolyCube.variables(2)
        p = 2*x**2 - 3*x*y + 1
        obtained = (-p).coef
        expected = [[-1, 0],
                    [ 0, 3],
                    [-2, 0]]
        self.assertTrue((obtained == expected).all(),
                        "bad negation:\n{0!s}".format(repr(obtained)))


class TestMVPolyCubeSubtract(unittest.TestCase) :

    def test_subtract(self) :
        x, _ = MVPolyCube.variables(2)
        p = 1 - x
        q = -(x - 1)
        self.assertTrue((p.coef == q.coef).all(),
                        "bad subtract:\n{0!s}\n{1!s}".format(repr(p.coef), repr(q.coef)))


class TestMVPolyCubeEval(unittest.TestCase) :

    @staticmethod
    def makep(x, y) :
        return (1 - x**2) * (1 + y) - 8

    def setUp(self) :
        x, y = MVPolyCube.variables(2, dtype=int)
        self.p = self.makep(x, y)
        self.x = [0, 1, -1, 0,  7, 3,  -3, 1]
        self.y = [0, 0,  0, 3, -1, 2, -10, 2]
        self.n = len(self.x)

    def test_eval_point(self) :
        for i in range(self.n) :
            obtained = self.p(self.x[i], self.y[i])
            expected = self.makep(self.x[i], self.y[i])
            self.assertTrue(expected == obtained,
                            "bad eval: {0!s}".format((repr(obtained))))

    def test_eval_array_1d(self) :
        obtained = self.p(self.x, self.y)
        expected = [self.makep(self.x[i], self.y[i]) for i in range(self.n)]
        self.assertTrue((expected == obtained).all(),
                        "bad eval: {0!s}".format((repr(obtained))))

    def test_eval_array_2d(self) :
        n = self.n
        x = np.reshape(self.x, (2, n/2))
        y = np.reshape(self.y, (2, n/2))
        obtained = self.p(x, y)
        self.assertTrue(obtained.shape == (2, n/2))
        obtained.shape = (n,)
        expected = [self.makep(self.x[i], self.y[i]) for i in range(self.n)]
        self.assertTrue((expected == obtained).all(),
                        "bad eval: {0!s}".format((repr(obtained))))

    def test_eval_badargs(self) :
        with self.assertRaises(RuntimeError) :
            self.p(self.x[1:], self.y)


class TestMVPolyCubeDiff(unittest.TestCase) :

    def test_diff_invariant(self) :
        x, y = MVPolyCube.variables(2, dtype=int)
        p  = x + 2*y
        expected = p.coef.copy()
        _ = p.diff(1,0)
        obtained = p.coef
        self.assertTrue((expected == obtained).all(),
                        "polynomial modified by diff {0!s}".format( \
                            (repr(obtained))))


class TestMVPolyCubeIntDiff(unittest.TestCase) :

    def test_intdif_random(self) :
        for dt in [float, complex] :
            shp = (9, 10, 11)
            c = np.random.randint(low=-10, high=10, size=shp)
            p = MVPolyCube(c, dtype=dt)
            expected = p.coef
            obtained = p.int(1, 1, 2).diff(1, 1, 2).coef
            self.assertTrue((np.abs(expected - obtained) < 1e-10).all(),
                            "bad integrate-differentiate \n{0!s}\n{1!s}".format(repr(obtained), repr(expected)))


class TestMVPolyCubeWendland(unittest.TestCase) :

    def setUp(self) :
        self.r, = MVPolyCube.variables(1, dtype=float)

    # these values are given exactly in Table 1 of Wendland, "Error
    # estimates for interpolation by compactly supported radial
    # basis functions of minimal degree", J. Approx. Theory, 93 (2),
    # 1998, 258--272

    def test_wendland_dim1_order0(self) :
        r = self.r
        expected = 1 - r
        obtained = MVPolyCube.wendland(1, 0)
        self.assertTrue(expected == obtained, "{0!s}".format((obtained)))

    def test_wendland_dim3_order0(self) :
        r = self.r
        expected = (1 - r)**2
        obtained = MVPolyCube.wendland(3, 0)
        self.assertTrue(expected == obtained, "{0!s}".format((obtained)))

    def test_wendland_dim5_order0(self) :
        r = self.r
        expected = (1 - r)**3
        obtained = MVPolyCube.wendland(5, 0)
        self.assertTrue(expected == obtained, "{0!s}".format((obtained)))

    # these are given only "up to a constant" op. cit., so we use a
    # custom assert -- if two polynomials are equal up to a constant
    # then the ratios of samples of those polynomials will be that
    # constant, we check that rmin/rmax =~ 1.0 so that the 'places'
    # argument of the built-in assertAlmostEqual tests for significant
    # (rather than decimal) places

    def assertEqualUpToConstant(self, p, q, **kwargs) :
        xs = [0.1, 0.3, 0.5, 0.7, 0.9]
        ratios = [p(x)/q(x) for x in xs]
        rmax = max(ratios)
        rmin = min(ratios)
        self.assertAlmostEqual(1.0, rmin/rmax, **kwargs)

    def test_wendland_dim1_order1(self) :
        r = self.r
        expected = (3*r + 1) * (1 - r)**3
        obtained = MVPolyCube.wendland(1, 1)
        self.assertEqualUpToConstant(expected, obtained)

    def test_wendland_dim1_order2(self) :
        r = self.r
        expected = (8*r*r + 5*r + 1) * (1 - r)**5
        obtained = MVPolyCube.wendland(1, 2)
        self.assertEqualUpToConstant(expected, obtained)

    def test_wendland_dim3_order1(self) :
        r = self.r
        expected = (4*r + 1) * (1 - r)**4
        obtained = MVPolyCube.wendland(3, 1)
        self.assertEqualUpToConstant(expected, obtained)

    def test_wendland_dim3_order2(self) :
        r = self.r
        expected = (35*r*r + 18*r + 3) * (1 - r)**6
        obtained = MVPolyCube.wendland(3, 2)
        self.assertEqualUpToConstant(expected, obtained)

    def test_wendland_dim3_order3(self) :
        r = self.r
        expected = (32*r*r*r + 25*r*r + 8*r + 1) * (1 - r)**8
        obtained = MVPolyCube.wendland(3, 3)
        self.assertEqualUpToConstant(expected, obtained)

    def test_wendland_dim5_order1(self) :
        r = self.r
        expected = (5*r + 1) * (1 - r)**5
        obtained = MVPolyCube.wendland(5, 1)
        self.assertEqualUpToConstant(expected, obtained)

    def test_wendland_dim5_order2(self) :
        r = self.r
        expected = (16*r*r + 7*r + 1) * (1 - r)**7
        obtained = MVPolyCube.wendland(5, 2)
        self.assertEqualUpToConstant(expected, obtained)


# this will not be added for a while, it is here just to
# check that mvpoly integration works for the author

def have_maxmodnb() :
    try:
        import maxmodnb
    except ImportError:
        return False
    return True

@unittest.skipUnless(have_maxmodnb(), "maxmodnb not installed")
class TestMVPolyCubeMaxmodnb(unittest.TestCase) :

    def test_maxmodnb_simple(self) :
        eps = 1e-10
        x, _ = MVPolyCube.variables(2, dtype=complex)
        p = x**2 + 1
        expected = 2.0
        obtained = p.maxmodnb(eps = eps)[0]
        self.assertTrue(abs(expected - obtained) < eps*expected,
                        "bad maxmodnb {0!s}".format(repr(obtained)))

    def test_maxmodnb_fifomax(self) :
        x, _ = MVPolyCube.variables(2, dtype=complex)
        p = x**2 + 1
        with self.assertRaises(RuntimeError) :
            p.maxmodnb(fifomax = 3)

    def test_maxmodnb_unknown_keyword(self) :
        x, _ = MVPolyCube.variables(2, dtype=complex)
        p = x**2 + 1
        with self.assertRaises(ValueError) :
            p.maxmodnb(nosuchvar = 3)

    def test_maxmodnb_no_positional_args(self) :
        x, _ = MVPolyCube.variables(2, dtype=complex)
        p = x**2 + 1
        with self.assertRaises(TypeError) :
            p.maxmodnb(3)


if __name__ == '__main__':
    unittest.main()
