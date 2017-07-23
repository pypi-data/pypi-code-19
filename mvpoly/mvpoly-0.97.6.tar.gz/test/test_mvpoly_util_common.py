import numpy as np
import scipy as sp
import mvpoly.util.common
import unittest

class TestMPUtilCommonCoerceTuple(unittest.TestCase):

    def test_scalar(self):
        a = mvpoly.util.common.coerce_tuple(1)
        self.assertIsInstance(a, tuple)
        self.assertEqual(a, (1,))

    def test_string(self):
        a = mvpoly.util.common.coerce_tuple("froob")
        self.assertIsInstance(a, tuple)
        self.assertEqual(a, ("froob",))

    def test_1_tuple(self):
        a = mvpoly.util.common.coerce_tuple((1,))
        self.assertIsInstance(a, tuple)
        self.assertEqual(a, (1,))

    def test_n_tuple(self):
        a = mvpoly.util.common.coerce_tuple((1, 2, 3))
        self.assertIsInstance(a, tuple)
        self.assertEqual(a, (1, 2, 3))

    def test_1_list(self):
        a = mvpoly.util.common.coerce_tuple([1])
        self.assertIsInstance(a, tuple)
        self.assertEqual(a, (1,))

    def test_n_list(self):
        a = mvpoly.util.common.coerce_tuple([1, 2, 3])
        self.assertIsInstance(a, tuple)
        self.assertEqual(a, (1, 2, 3))

    def test_1_set(self):
        a = mvpoly.util.common.coerce_tuple(set([1]))
        self.assertIsInstance(a, tuple)
        self.assertEqual(a, (1,))

    def test_n_set(self):
        a = mvpoly.util.common.coerce_tuple(set([1, 2, 3]))
        self.assertIsInstance(a, tuple)
        self.assertEqual(a, (1, 2, 3))


class TestMPUtilCommonAsNumpyScalar(unittest.TestCase):

    def test_int64(self):
        a = mvpoly.util.common.as_numpy_scalar(3)
        self.assertIsInstance(a, np.int64)
        self.assertEqual(a, 3)

    def test_float64(self):
        a = mvpoly.util.common.as_numpy_scalar(3.0)
        self.assertIsInstance(a, np.float64)
        self.assertEqual(a, 3.0)

    def test_kwd_dtype_int64(self):
        a = mvpoly.util.common.as_numpy_scalar(3.0, dtype=np.int64)
        self.assertIsInstance(a, np.int64)
        self.assertEqual(a, 3)

    def test_kwd_dtype_float64(self):
        a = mvpoly.util.common.as_numpy_scalar(3, dtype=np.float64)
        self.assertIsInstance(a, np.float64)
        self.assertEqual(a, 3)


class TestMPUtilCommonBinom(unittest.TestCase):

    def test_binom_reference(self):
        for n, i in [(3, 2), (5, 0), (7, 6)]:
            a = mvpoly.util.common.binom(n, i)
            b = int(round(sp.special.binom(n, i)))
            self.assertTrue(a == b, "binomial against reference")

class TestMPUtilCommonKronn(unittest.TestCase):

    def test_kronn_simple(self):
        a = np.array([1, -1])
        b = np.array([1, 1])
        expected = np.array([1, 1, 1, 1, -1, -1, -1, -1])
        obtained = mvpoly.util.common.kronn(a, b, b)
        self.assertTrue((expected == obtained).all(),
                        "bad kronn:\n{0!s}".format(repr(obtained)))

    def test_kronn_2_arg(self):
        a = np.array([2, 3])
        b = np.array([4, 1])
        expected = np.kron(a, b)
        obtained = mvpoly.util.common.kronn(a, b)
        self.assertTrue((expected == obtained).all(),
                        "bad kronn:\n{0!s}".format(repr(obtained)))

    def test_kronn_dtype(self):
        for dt in (int, float):
            a = np.array([[2, 3], [4, 5]], dtype=dt)
            expected = dt
            obtained = mvpoly.util.common.kronn(a, a, a).dtype
            self.assertTrue(expected == obtained,
                            "bad kronn dtype:\n{0!s}".format(repr(obtained)))


class TestMPUtilCommonMonimialIndices(unittest.TestCase):

    def test_monomial_indices_count(self):
        data = {
            (1, 0) : 1,
            (1, 1) : 2,
            (1, 2) : 3,
            (3, 0) : 1,
            (3, 1) : 4,
            (3, 2) : 10,
            (3, 3) : 20,
            (3, 4) : 35,
            (4, 0) : 1,
            (4, 1) : 5,
            (4, 2) : 15,
            (4, 3) : 35,
            (4, 4) : 70,
        }
        for arg, expected in data.items():
            obtained = len(list(mvpoly.util.common.monomial_indices(*arg)))
            msg = "bad ({0:d}, {1:d}) monomial count:\n{2:d}".format(arg[0], arg[1], obtained)
            self.assertTrue(expected == obtained, msg)

    def test_monomial_indices_explicit(self):
        data = {
            (1, 0) : [(0,)],
            (1, 1) : [(0,), (1,)],
            (1, 2) : [(0,), (1,), (2,)],
            (2, 0) : [(0, 0)],
            (2, 1) : [(0, 0), (1, 0), (0, 1)],
            (2, 2) : [(0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2)],
        }
        for arg, expected in data.items():
            obtained = list(mvpoly.util.common.monomial_indices(*arg))
            msg = "{0!s} != {1!s}".format(repr(expected), repr(obtained))
            self.assertTrue(expected == obtained, msg)

    def test_monomial_bad_num_vars(self):
        for n in (-2, -1, 0):
            with self.assertRaises(ValueError):
                list(mvpoly.util.common.monomial_indices(n, 2))

    def test_monomial_bad_max_order(self):
        for k in (-3, -2, -1):
            with self.assertRaises(ValueError):
                list(mvpoly.util.common.monomial_indices(2, k))


if __name__ == '__main__':
    unittest.main()
