from mvpoly.rbf import (RBFGaussian,
                        RBFMultiQuadric,
                        RBFInverseMultiQuadric,
                        RBFThinPlateSpline,
                        RBFWendland)
from mvpoly.cube import MVPolyCube
from mvpoly.dict import MVPolyDict
import mvpoly.util.version as version
import numpy as np
import unittest

# for selecting subsets of the intepolation classes with particular
# properties

def rbf_classes(*args):
    classes = {
        RBFGaussian : ['dense', 'epsilon'],
        RBFMultiQuadric : ['dense', 'epsilon'],
        RBFInverseMultiQuadric : ['dense', 'epsilon'],
        RBFThinPlateSpline : ['dense'],
        RBFWendland : ['sparse'],
    }

    # silently skip Wendland RBF tests for old scipy versions,
    # we would like to verbosely skip them, but we would need
    # to rewrite all the tests to be per-class so that skipping
    # Wendland does not skip all the others ... in ruby one
    # would do this with create_method, but in python ?

    if not version.at_least('scipy', (0, 17, 0)):
        classes.pop(RBFWendland)

    if args:
        matching = []
        for key, value in classes.items():
            if all( arg in value for arg in args):
                matching.append(key)
    else:
        matching = classes.keys()

    return matching

POLY_CLASSES = (MVPolyCube, MVPolyDict)

class TestMVPolyRBF(unittest.TestCase):

    # Check that an RBF interpolates the nodes (1D)

    def check_interp_on_nodes_1d(self, rbf_class, poly_class, large):
        eps = 1e-10
        x = np.linspace(0, 10, 9)
        f = np.sin(x)
        rbf = rbf_class(x, f, poly_class=poly_class)
        fi = rbf(x, large=large)
        self.assertTrue(np.allclose(f, fi, atol=eps),
                        "{0!s}: on-node 1D".format(rbf.name))

    def test_rbf_interp_on_nodes_1d(self):
        for rbf_class in rbf_classes():
            for poly_class in POLY_CLASSES:
                for large in (True, False):
                    self.check_interp_on_nodes_1d(rbf_class, poly_class, large)

    # Check that an RBF interpolates the nodes (2D)

    def check_interp_on_nodes_2d(self, rbf_class, poly_class, large):
        eps = 1e-10
        x = np.random.rand(50, 1)*4 - 2
        y = np.random.rand(50, 1)*4 - 2
        f = x*np.exp(-x**2 - 1j*y**2)
        rbf = rbf_class(x, y, f, poly_class=poly_class)
        fi = rbf(x, y, large=large)
        fi.shape = x.shape
        self.assertTrue(np.allclose(f, fi, atol=eps),
                        "{0!s}: on-node 2D".format(rbf.name))

    def test_rbf_interp_on_nodes_2d(self):
        for rbf_class in rbf_classes('dense'):
            for poly_class in POLY_CLASSES:
                for large in (True, False):
                    self.check_interp_on_nodes_2d(rbf_class, poly_class, large)

    # Check that an RBF instance approximates a smooth function
    # away from the nodes.

    def check_interp_off_nodes_1d(self, rbf_class, poly_class, large, atol):
        x = np.linspace(0, 10, 9)
        f = np.sin(x)
        rbf = rbf_class(x, f, poly_class=poly_class)
        x_fine = np.linspace(0, 10, 100)
        f0 = rbf(x_fine, large=large)
        f1 = np.sin(x_fine)
        msg = "abs-diff: {0:f}".format(abs(f0 - f1).max())
        self.assertTrue(np.allclose(f0, f1, atol=atol),
                        "{0!s}: off-nodes {1!s}".format(rbf.name, msg))

    def test_rbf_interp_off_nodes_1d(self):
        tol = {
            RBFGaussian : 0.15,
            RBFMultiQuadric : 0.10,
            RBFInverseMultiQuadric : 0.15,
            RBFThinPlateSpline : 0.10,
            RBFWendland : 0.15,
        }
        for rbf_class in rbf_classes('dense'):
            for poly_class in POLY_CLASSES:
                for large in (True, False):
                    args = (rbf_class, poly_class, large, tol.get(rbf_class))
                    self.check_interp_off_nodes_1d(*args)

    # Check that a vertical shift of interpolation points gives
    # rise to the same shift of the interpolation (or of the
    # approximant, when smooth != 0).

    def check_shift_invariance(self, rbf_class, poly_class, smooth):
        eps = 1e-10
        n = 10
        x = np.linspace(0, n-1, n)
        f = np.random.randn(len(x))
        rbf0 = rbf_class(x, f, smooth=smooth, poly_class=poly_class)
        rbf1 = rbf_class(x, f + 1, smooth=smooth, poly_class=poly_class)
        x_fine = np.linspace(0, n-1, 5*n)
        f0 = rbf0(x_fine) + 1
        f1 = rbf1(x_fine)
        self.assertTrue(np.allclose(f0, f1, atol=eps),
                        '{0!s} shift invariance'.format(rbf0.name))

    def test_rbf_shift_invariance(self):
        for rbf_class in rbf_classes():
            for poly_class in POLY_CLASSES:
                for smooth in [0, 1e-3, 1e-1]:
                    self.check_shift_invariance(rbf_class, poly_class, smooth)

    # Check that an affine transform of interpolation points
    # gives rise to the same for the interpolation (or of the
    # approximant, when smooth != 0).

    def check_affine_invariance(self, rbf_class, poly_class, smooth):
        eps = 1e-10
        n = 10
        x = np.linspace(0, n-1, n)
        f = np.random.randn(len(x))
        rbf0 = rbf_class(x, f, smooth=smooth, poly_class=poly_class)
        rbf1 = rbf_class(x, f + 3*x + 2, smooth=smooth, poly_class=poly_class)
        x_fine = np.linspace(0, n-1, 5*n)
        f0 = rbf0(x_fine) + 3*x_fine + 2
        f1 = rbf1(x_fine)
        self.assertTrue(np.allclose(f0, f1, atol=eps),
                        '{0!s}: affine invariance'.format(rbf0.name))

    def test_rbf_affine_invariance(self):
        for rbf_class in rbf_classes():
            for poly_class in POLY_CLASSES:
                for smooth in [0, 1e-3, 1e-1]:
                    self.check_affine_invariance(rbf_class, poly_class, smooth)

    # When using a small positive smoothing parameter on a coarsely
    # discretised step, we expect nodes away from the step to be
    # close (but not that close) to the data samples. (This test will
    # fail if the the `sign` in the smoothing setup is reversed)

    def check_positive_smoothing(self, rbf_class, poly_class):
        eps = 0.03
        n = 10
        x = np.linspace(0, n-1, n)
        f = np.array([-1 if k < n/2 else 1 for k in x], dtype=np.float)
        rbf = rbf_class(x, f, smooth=1e-4, poly_class=poly_class)
        offstep = list(range(0, n//2-1)) + list(range(n//2+1, n))
        x_offstep = x[offstep]
        f0 = rbf(x_offstep)
        f1 = f[offstep]
        msg = "abs-diff: {0:f}".format(abs(f0 - f1).max())
        self.assertTrue(np.allclose(f0, f1, atol=eps),
                        "{0!s}: positive smoothing ({1!s})".format(rbf.name, msg))

    def test_rbf_positive_smoothing(self):
        for rbf_class in rbf_classes():
            for poly_class in POLY_CLASSES:
                self.check_positive_smoothing(rbf_class, poly_class)

    # Check that an RBF instances of classes which use the epsilon
    # parameter can be constructed using a None value of (and that
    # results in epsilon being chosen non-zero)

    def check_epsilon_auto(self, rbf_class):
        x = np.linspace(0, 10, 9)
        f = np.sin(x)
        rbf = rbf_class(x, f, epsilon=None)
        self.assertTrue(rbf.epsilon > 0,
                        '{0!s}: non-positive epsilon'.format(rbf.name))

    def test_rbf_epsilon_auto(self):
        for rbf_class in rbf_classes('epsilon'):
            self.check_epsilon_auto(rbf_class)

    # Check that an RBF instance can be constructed using
    # with radius absent or a None value (and that results
    # in radius being chosen non-zero)

    def check_radius_none(self, rbf_class):
        x = np.linspace(0, 10, 9)
        f = np.sin(x)
        rbf = rbf_class(x, f, radius=None)
        self.assertTrue(rbf.radius > 0,
                        '{0!s}: non-positive radius'.format(rbf.name))

    def check_radius_absent(self, rbf_class):
        x = np.linspace(0, 10, 9)
        f = np.sin(x)
        rbf = rbf_class(x, f)
        self.assertTrue(rbf.radius > 0,
                        '{0!s}: non-positive radius'.format(rbf.name))

    def test_rbf_radius_auto(self):
        for rbf_class in rbf_classes('sparse'):
            self.check_radius_none(rbf_class)
            self.check_radius_absent(rbf_class)

    # Check that an RBF instance with default epsilon/radius is not
    # subject to overshoot

    def check_epsilon_stability(self, rbf_class, poly_class):
        np.random.seed(1234)
        x = np.linspace(0, 10, 50)
        f = x + 4.0 * np.random.randn(len(x))
        rbf = rbf_class(x, f, poly_class=poly_class)
        x0 = np.linspace(0, 10, 1000)
        f0 = rbf(x0)
        self.assertTrue(np.abs(f0-x0).max() / np.abs(f-x).max() < 1.2,
                        "{0!s}: default epsilon/radius stability".format(rbf.name))

    def test_rbf_epsilon_stability(self):
        for rbf_class in rbf_classes('epsilon'):
            for poly_class in POLY_CLASSES:
                self.check_epsilon_stability(rbf_class, poly_class)

    # check that an RBF instance with poly_order=None has a poly
    # method of None, an that the rbf method is identical to the
    # call method

    def check_poly_order_none(self, rbf_class):
        x = np.linspace(0, 10, 9)
        f = np.sin(x)
        rbf = rbf_class(x, f, poly_order=None)
        self.assertTrue(rbf.poly is None, 'poly method not none')
        self.assertTrue(rbf.rbf(np.array(5)) == rbf(5), 'rbf method != call')

    def test_rbf_poly_order_none(self):
        for rbf_class in rbf_classes():
            self.check_poly_order_none(rbf_class)

    # check that an RBF instance with specified poly_order has a
    # poly method which is at most of that degree

    def check_poly_order_natural(self, rbf_class, n):
        x = np.linspace(0, 10, 9)
        f = np.sin(x)
        rbf = rbf_class(x, f, poly_order=n)
        self.assertTrue(rbf.poly is not None, 'poly method none')
        self.assertTrue(rbf.poly.degree <= n, 'poly degree wrong')

    def test_rbf_poly_order_natural(self):
        for rbf_class in rbf_classes():
            for n in range(4):
                self.check_poly_order_natural(rbf_class, n)

    # check that attempting to create an RBF instance with a negative
    # specified poly_order raises a ValueError

    def test_rbf_poly_order_negative(self):
        x = np.linspace(0, 10, 9)
        f = np.sin(x)
        for rbf_class in rbf_classes():
            with self.assertRaises(ValueError):
                rbf_class(x, f, poly_order=-1)
            for poly_class in POLY_CLASSES:
                with self.assertRaises(ValueError):
                    rbf_class(x, f, poly_order=-1, poly_class=poly_class)

    # check the dtype of the interpolant

    def check_poly_dtype_real(self, rbf_class):
        x = np.linspace(0, 10, 9)
        f = np.sin(x)
        rbf = rbf_class(x, f)
        fi = rbf(5.0)
        self.assertTrue(fi.dtype == np.float64, 'dtype {0!s}'.format(fi))

    def check_poly_dtype_complex(self, rbf_class):
        x = np.linspace(0, 10, 9)
        f = np.sin(x) * 1j
        rbf = rbf_class(x, f)
        fi = rbf(5.0)
        self.assertTrue(fi.dtype == np.complex128, 'dtype {0!s}'.format(fi))

    def test_rbf_dtype(self):
        for rbf_class in rbf_classes('dense'):
            self.check_poly_dtype_real(rbf_class)
            self.check_poly_dtype_complex(rbf_class)
