import unittest
from numpy import array
from numpy.testing import assert_array_equal
import polymath

class Testpolymod(unittest.TestCase):

    def test_01(self):
        test_array = array([1])
        f = array([1, 0, 1, 0, 0, 1, 1, 0, 1])
        assert_array_equal(
            polymath.polymod(test_array, f),
            [1],
            "Polymath modulo of 1 % 101001101 fails"
        )

    def test_02(self):
        test_array = array([0, 0, 0, 0, 0, 0, 0, 1])
        f = array([1, 0, 1, 0, 0, 1, 1, 0, 1])
        assert_array_equal(
            polymath.polymod(test_array, f),
            [1],
            "Polymath modulo of 00000001 % 101001101 fails"
        )

    def test_03(self):
        test_array = array([0, 0, 0, 0, 0, 0, 0, 3])
        f = array([1, 0, 1, 0, 0, 1, 1, 0, 1])
        assert_array_equal(
            polymath.polymod(test_array, f),
            [1],
            "Polymath modulo of 3 % 101001101 fails"
        )

    def test_04(self):
        test_array = array([0, 0, 0, 0, 0, 0, 0, 0])
        f          = array([1, 0, 1, 0, 0, 1, 1, 0, 1])
        assert_array_equal(
            polymath.polymod(test_array, f),
            [0],
            "Polymath modulo of 00000000 % 101001101 fails"
        )

    def test_05(self):
        test_array = array([0])
        f          = array([1, 0, 1, 0, 0, 1, 1, 0, 1])
        assert_array_equal(
            polymath.polymod(test_array, f),
            [0],
            "Polymath modulo of 0 % 101001101 fails"
        )

    def test_06(self):
        test_array = array([1, 0, 1, 0, 0, 0, 1, 0, 0])
        f =          array([1, 0, 1, 0, 0, 1, 1, 0, 1])
        assert_array_equal(
            polymath.polymod(test_array, f),
            [1, 0, 0, 1],
            "Polymath modulo of 101000100 % 101001101 fails"
        )

    def test_07(self):
        test_array = array([0, 0, 0, 0, 0, 0, 1, 1, 1])
        f =          array([1, 0, 1, 0, 0, 1, 1, 0, 1])
        assert_array_equal(
            polymath.polymod(test_array, f),
            [1, 1, 1],
            "Polymath modulo of 111 % 101001101 fails"
        )