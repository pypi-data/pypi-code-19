import math
import unittest

from pyrogi.util import Vec2

class TestVec2(unittest.TestCase):
    def test_init(self):
        self.assertEqual(Vec2(1, 4.5), Vec2((1, 4.5)))
        self.assertNotEqual(Vec2(1, 4.5), Vec2((1, 4.51)))
        self.assertEqual(Vec2((2, -3922)), Vec2(2, -3922))
        self.assertNotEqual(Vec2((2, -3922)), Vec2(2, 3922))

    def test_vector_multiplication(self):
        self.assertEqual(Vec2(0, 0)*Vec2(1, 5), Vec2(0, 0))
        self.assertEqual(Vec2(1, 5)*Vec2(0, 0), Vec2(0, 0))

        self.assertEqual(Vec2(1.0, 1)*Vec2(123456.3020, -987654), Vec2(123456.3020, -987654))
        self.assertEqual(Vec2(123456, -987654)*Vec2(1, 1), Vec2(123456, -987654))

        self.assertEqual(Vec2(6, 2)*Vec2(1.5, -6), Vec2(9, -12))
        self.assertEqual(Vec2(1.5, -6)*Vec2(6, 2), Vec2(9, -12))

    def test_scalar_multiplication(self):
        self.assertEqual(0*Vec2(1, 594.39), Vec2(0, 0))
        self.assertEqual(Vec2(1, 594.39)*0, Vec2(0, 0))

        self.assertEqual(1*Vec2(2893.983, 18320.901290), Vec2(2893.983, 18320.901290))
        self.assertEqual(Vec2(2893.983, 18320.901290)*1, Vec2(2893.983, 18320.901290))

        self.assertEqual(2.3939*Vec2(-0.245, 862.254), Vec2(-0.5865055, 2064.1498506))
        self.assertEqual(Vec2(-0.245, 862.254)*2.3939, Vec2(-0.5865055, 2064.1498506))

    def test_vector_true_division(self):
        self.assertEqual(Vec2(0, 0)/Vec2(-12985, 18092.8201), Vec2(0, 0))
        self.assertRaises(ZeroDivisionError, Vec2.__truediv__, Vec2(-12985, 18092.8201), Vec2(0, 0))

        self._assertVectorsEqual(Vec2(1, 1)/Vec2(3, 5.2), Vec2(0.3333333, 0.1923077))
        self.assertEqual(Vec2(3, 5.2)/Vec2(1, 1), Vec2(3, 5.2))

        self._assertVectorsEqual(Vec2(1184.929, 4)/Vec2(2939.393, -87562.1705), Vec2(0.4031203, -0.000045681828))
        self._assertVectorsEqual(Vec2(-2939.393, -87562.1705)/Vec2(1184.929, -4), Vec2(-2.48064901, 21890.542625))

    def test_vector_floor_division(self):
        self.assertEqual(Vec2(0, 0)//Vec2(-12985, 18092.8201), Vec2(0, 0))
        self.assertRaises(ZeroDivisionError, Vec2.__floordiv__, Vec2(-12985, 18092.8201), Vec2(0, 0))

        self.assertEqual(Vec2(1, 1)//Vec2(3, 5.2), Vec2(0, 0))
        self.assertEqual(Vec2(3, 5.2)//Vec2(1, 1), Vec2(3, 5))

        self.assertEqual(Vec2(1184.929, 4)//Vec2(2939.393, -87562.1705), Vec2(0, -1))
        self.assertEqual(Vec2(-2939.393, -87562.1705)//Vec2(1184.929, -4), Vec2(-3, 21890))

    def test_scalar_true_division(self):
        self.assertEqual(0/Vec2(3, 5.9392), Vec2(0, 0))
        self.assertRaises(ZeroDivisionError, Vec2.__truediv__, Vec2(3, 5.9392), 0)
        self.assertRaises(ZeroDivisionError, Vec2.__rtruediv__, Vec2(0, 0), 3)

        self._assertVectorsEqual(1/Vec2(3.2, 9), Vec2(0.3125, 0.1111111))
        self.assertEqual(Vec2(3.2, 9)/1, Vec2(3.2, 9))

        self._assertVectorsEqual(2/Vec2(4, -6.2), Vec2(0.5, -0.3225806))
        self._assertVectorsEqual(Vec2(4, 6.2)/-2.1, Vec2(-1.9047619, -2.952381))

    def test_scalar_floor_division(self):
        self.assertEqual(0//Vec2(3, 5.9392), Vec2(0, 0))
        self.assertRaises(ZeroDivisionError, Vec2.__floordiv__, Vec2(3, 5.9392), 0)
        self.assertRaises(ZeroDivisionError, Vec2.__rfloordiv__, Vec2(0, 0), 3)

        self.assertEqual(1//Vec2(3.2, 9), Vec2(0, 0))
        self.assertEqual(Vec2(3.2, 9)//1, Vec2(3, 9))

        self.assertEqual(2//Vec2(4, -6.2), Vec2(0, -1))
        self.assertEqual(Vec2(4, 6.2)//-2.1, Vec2(-2, -3))

    def test_addition(self):
        self.assertEqual(Vec2(0, 0)+Vec2(34.494, 2.292), Vec2(34.494, 2.292))
        self.assertEqual(Vec2(34.494, 2.292)+Vec2(0, 0), Vec2(34.494, 2.292))

        self._assertVectorsEqual(Vec2(-3, -5.6)+Vec2(-8.54, -0.43), Vec2(-11.54, -6.03))

    def test_subtraction(self):
        self.assertEqual(Vec2(0, 0)-Vec2(34.494, 2.292), Vec2(-34.494, -2.292))
        self.assertEqual(Vec2(34.494, 2.292)-Vec2(0, 0), Vec2(34.494, 2.292))

        self._assertVectorsEqual(Vec2(4, 2.1)-Vec2(-6, 1.39), Vec2(10, 0.71))
        self.assertEqual(Vec2(-5.2, -9.6)-Vec2(4, -2.3), Vec2(-9.2, -7.3))

    def test_negation(self):
        self.assertEqual(-Vec2(0, 0), Vec2(0, 0))
        self.assertEqual(-Vec2(-1, 1), Vec2(1, -1))
        self.assertEqual(-Vec2(-2.34, 6), Vec2(2.34, -6))
        self.assertEqual(-Vec2(-3.6, -0.945), Vec2(3.6, 0.945))

    def test_dot_product(self):
        self.assertEqual(Vec2(0, 0).dot(Vec2(0, 0)), 0)
        self.assertEqual(Vec2(1, 1).dot(Vec2(0, 0)), 0)
        self.assertEqual(Vec2(0, 0).dot(Vec2(1, 1)), 0)

        self.assertEqual(Vec2(1, 1).dot(Vec2(1, 1)), 2)
        self.assertEqual(Vec2(-3, 2.5).dot(Vec2(6, -6)), -33)
        self.assertEqual(Vec2(-3, -1.5).dot(Vec2(-2, -8)), 18)
        self.assertEqual(Vec2(4, 0).dot(Vec2(-6, 11)), -24)

    def test_normalized(self):
        self.assertRaisesRegex(ValueError, 'Cannot normalize a vector of magnitude zero.', Vec2.normalized, Vec2(0, 0))

        self.assertEqual(Vec2(-135, 0).normalized(), Vec2(-1, 0))
        self.assertEqual(Vec2(2345, 0).normalized(), Vec2(1, 0))
        self.assertEqual(Vec2(0, -12000).normalized(), Vec2(0, -1))
        self.assertEqual(Vec2(0, 2394).normalized(), Vec2(0, 1))

        self._assertVectorsEqual(Vec2(1, 1).normalized(), Vec2(1/math.sqrt(2), 1/math.sqrt(2)))
        self._assertVectorsEqual(Vec2(-5, -2).normalized(), Vec2(-5/math.sqrt(29), -2/math.sqrt(29)))
        self._assertVectorsEqual(Vec2(7.4, -1.12).normalized(), Vec2(0.9887395, -0.1496471))
        self._assertVectorsEqual(Vec2(-3, 12).normalized(), Vec2(-1/math.sqrt(17), 4/math.sqrt(17)))

    def test_magnitude(self):
        self.assertEqual(Vec2(0, 0).magnitude(), 0)
        self.assertEqual(Vec2(1, 0).magnitude(), 1)
        self.assertEqual(Vec2(0, 1).magnitude(), 1)

        self.assertEqual(Vec2(7, 0).magnitude(), 7)
        self.assertEqual(Vec2(-164, 0).magnitude(), 164)
        self.assertEqual(Vec2(0, 38294).magnitude(), 38294)
        self.assertEqual(Vec2(0, -23.645).magnitude(), 23.645)

        self.assertEqual(Vec2(1, 1).magnitude(), math.sqrt(2))
        self.assertEqual(Vec2(12, -16).magnitude(), 20)
        self.assertAlmostEqual(Vec2(-4.7, 10.02).magnitude(), 11.0675381)
        self.assertEqual(Vec2(20, 48).magnitude(), 52)

    def test_equals(self):
        self.assertTrue(Vec2(0, 0) == Vec2(0, 0))
        self.assertTrue(Vec2(-2, 5) == Vec2(-2, 5))
        self.assertTrue(Vec2(2.3449, 281.8929203) == Vec2(2.3449, 281.8929203))

        self.assertFalse(Vec2(5, 2) == Vec2(-5, 2))
        self.assertFalse(Vec2(1.2364, 2.02) == Vec2(1.2364, 2.0201))

    def test_not_equals(self):
        self.assertFalse(Vec2(0, 0) != Vec2(0, 0))
        self.assertFalse(Vec2(-2, 5) != Vec2(-2, 5))
        self.assertFalse(Vec2(2.3449, 281.8929203) != Vec2(2.3449, 281.8929203))

        self.assertTrue(Vec2(5, 2) != Vec2(-5, 2))
        self.assertTrue(Vec2(1.2364, 2.02) != Vec2(1.2364, 2.0201))

    def test_to_tuple(self):
        self.assertEqual(Vec2(0, 0).to_tuple(), (0, 0))
        self.assertEqual(Vec2(-2.394, 7.00054).to_tuple(), (-2.394, 7.00054))

    def _assertVectorsEqual(self, vec1, vec2):
        self.assertAlmostEqual(vec1.x, vec2.x)
        self.assertAlmostEqual(vec1.y, vec2.y)
