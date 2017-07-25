import unittest
import numpy as np
from numpy.testing import assert_allclose

from diff2d.core import evolve

_default = np.array([[0., 0., 0., 0., 0.],
                     [0., 0., 0.01, 0., 0.],
                     [0., 0.01, 0.96, 0.01, 0.],
                     [0., 0., 0.01, 0., 0.],
                     [0., 0., 0., 0., 0.]])

_01dt_1D = np.array([[0., 0., 0., 0., 0.],
                     [0., 0., 0.1, 0., 0.],
                     [0., 0.1, 0.6, 0.1, 0.],
                     [0., 0., 0.1, 0., 0.],
                     [0., 0., 0., 0., 0.]])

_001dt_05D = np.array([[0., 0., 0., 0., 0.],
                       [0., 0., 0.005, 0., 0.],
                       [0., 0.005, 0.98, 0.005, 0.],
                       [0., 0., 0.005, 0., 0.],
                       [0., 0., 0., 0., 0.]])

_u_001dt_1D = np.array([[0.96, 0.01, 0., 0., 0.01],
                        [0.01, 0., 0., 0., 0.],
                        [0., 0., 0., 0., 0.],
                        [0., 0., 0., 0., 0.],
                        [0.01, 0., 0., 0., 0.]])


class EvolveTest(unittest.TestCase):

    def setUp(self):
        self.initial = np.zeros((5,5))
        self.initial[2,2] = 1

    def test_default(self):
        """
        Test the default parameters
        """
        assert_allclose(evolve(self.initial, 0.01, 1), _default, atol=1e-07)

    def test_dt(self):
        """
        Test the dt parameter
        """
        assert_allclose(evolve(self.initial, 0.1, 1), _01dt_1D, atol=1e-07)

    def test_D(self):
        """
        Test the D parameter
        """
        assert_allclose(evolve(self.initial, 0.01, 0.5), _001dt_05D, atol=1e-07)

    def test_u(self):
        """
        Test different initial value set.
        """
        u = np.zeros((5,5))
        u[0,0] = 1
        assert_allclose(evolve(u, 0.01, 1), _u_001dt_1D, atol=1e-07)

if __name__ == '__main__':
    unittest.main()
