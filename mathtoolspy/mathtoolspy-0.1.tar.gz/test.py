'''
Created on 16.12.2016

@author: MarcusSteinkamp
'''
import unittest
from math import exp, cos

from mathtoolspy.distribution.normal_distribution import density_normal_dist, cdf_abramowitz_stegun
from mathtoolspy.integration.gauss_kronrod_integrator import GaussKronrodIntegrator as gauss_kronrod
from mathtoolspy.integration.gauss_lobatto_integrator import GaussLobattoIntegrator as gauss_lobatto
from mathtoolspy.integration.simplex_integrator import SimplexIntegrator as simplex
from mathtoolspy.utils.math_fcts import CompositionFct
from mathtoolspy.utils.mathconst import PI

from mathtoolspy.integration.gauss_legendre_integrator import GaussLegendreIntegrator as gauss_legendre
from mathtoolspy.solver.optimizer import Optimizer1Dim, Constraint, TangentsTransformation, TangentsInverseTransformation, \
    OptimizerResult
from mathtoolspy.solver.minimize_algorithm_1dim_brent import minimize_algorithm_1dim_brent as brent
from mathtoolspy.solver.minimize_algorithm_1dim_golden import minimize_algorithm_1dim_golden as golden
from mathtoolspy.solver.minimum_bracketing import minimum_bracketing, mn_brak
from mathtoolspy.solver.analytic_solver import roots_of_cubic_polynom

from mathtoolspy import Surface

def generate_integration_tests():
    def print_(f, msg):
        f.write("\t" + msg + "\n")

    integrators_names = {"gauss_kronrod": "gauss_kronrod()",
                         "simplex": "simplex()", "gauss_legendre": "gauss_legendre()",
                         "gauss_lobatto": "gauss_lobatto()",
                         "simplex_steps_1000": "simplex(steps=1000)",
                         "gauss_legendre_steps_500": "gauss_legendre(steps=500)",
                         "gauss_lobatto_max_iter_127": "gauss_lobatto(max_number_of_iterations = 255, abs_tolerance = 1.0e-7)",
                         "gauss_kronrod_check_rel_tolerance": "gauss_kronrod(check_abs_tolerance = False, check_rel_tolerance = True)",
                         "gauss_kronrod_check_abs_tolerance_check_rel_tolerance": "gauss_kronrod(check_abs_tolerance = True, check_rel_tolerance = True)"
                         }
    fcts_names = ("lambda x:2", "lambda x:x*x", "lambda x:exp(-x*x)",
                  "lambda x: x*x*x if x > 1 else x-2")

    integrators = {'gauss_legendre': gauss_legendre(), 'gauss_lobatto': gauss_lobatto(),
                   'simplex_steps_1000': simplex(steps=1000), 'simplex': simplex(), 'gauss_kronrod': gauss_kronrod(),
                   'gauss_legendre_steps_500': gauss_legendre(steps=500),
                   'gauss_kronrod_check_abs_tolerance_check_rel_tolerance': gauss_kronrod(check_abs_tolerance=True,
                                                                                          check_rel_tolerance=True),
                   'gauss_lobatto_max_iter_127': gauss_lobatto(max_number_of_iterations=255, abs_tolerance=1.0e-7),
                   'gauss_kronrod_check_rel_tolerance': gauss_kronrod(check_abs_tolerance=False,
                                                                      check_rel_tolerance=True)}
    fcts = (lambda x: 2, lambda x: x * x, lambda x: exp(-x * x), lambda x: x * x * x if x > 1 else x - 2)

    '''
    s = []
    for int_name, i in integrators_names.items():
        s.append("'" + int_name + "':" + i)
    print("integrators = {" + ", ".join(s) + "}")
    print("fcts = (" + ", ".join(fcts_names) + ")")
        
    
    '''
    integration_boundaries = ((-1.0, 2.0), (0.0, 1.0), (-100.0, 99.0))
    file_name = r"/Users/MarcusSteinkamp/Documents/integrator_test_code.txt"
    fi = open(file_name, "w")
    c = 0
    i_fct = 0
    for n, i in integrators_names.items():
        i_fct = 0
        for f in fcts_names:
            for l, u in integration_boundaries:
                print_(fi, "def test_integrator_" + str(c).zfill(3) + "_" + n + "(self):")
                print_(fi, "\tfct = " + f)
                print_(fi, "\tintegrator = " + i)
                print_(fi, "\tresult = integrator(fct, " + str(l) + ", " + str(u) + ")")
                print_(fi, "\tbenchmark = " + "{:18.9f}".format(integrators[n](fcts[i_fct], l, u)))
                print_(fi, "\tself.assertAlmostEqual(benchmark, result, 8)")
                print_(fi, "")
                c = c + 1
            i_fct = i_fct + 1


class Test(unittest.TestCase):
    # ----------------------- INTEGRATION TEST ------------------------------
    '''

    def test_gen(self):
        generate_integration_tests()
    '''

    def test_simplex_0(self):
        result = simplex(steps=1000)(lambda x: x * x, -1.0, 1.0)
        self.assertAlmostEqual(0.6666679999999994, result, 10)

    def test_simplex_1(self):
        result = simplex(steps=1000)(self._init_polynom(), -4.0, 5.0)
        self.assertAlmostEqual(802.8051029980307, result, 10)

    def test_integrator_compare(self):
        i0 = simplex(steps=5000)
        i1 = gauss_kronrod()
        # i2 = gauss_legendre(steps = 1000) # gauss_legendre calculates bad.
        i3 = gauss_lobatto()
        fct = lambda x: cos(x)
        l = 0
        u = PI / 2.0
        r0 = i0(fct, l, u)
        r1 = i1(fct, l, u)
        # r2 = i2(fct, l, u)
        r3 = i3(fct, l, u)
        benchmark = 1.0
        self.assertAlmostEqual(r0, benchmark, 6)
        self.assertAlmostEqual(r1, benchmark, 6)
        self.assertAlmostEqual(r3, benchmark, 6)

    def test_integrator_000_gauss_legendre(self):
        fct = lambda x: 2
        integrator = gauss_legendre()
        result = integrator(fct, -1.0, 2.0)
        benchmark = 5.99999999994
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_001_gauss_legendre(self):
        fct = lambda x: 2
        integrator = gauss_legendre()
        result = integrator(fct, 0.0, 1.0)
        benchmark = 1.99999999998
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_002_gauss_legendre(self):
        fct = lambda x: 2
        integrator = gauss_legendre()
        result = integrator(fct, -100.0, 99.0)
        benchmark = 397.999999996
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_003_gauss_legendre(self):
        fct = lambda x: x * x
        integrator = gauss_legendre()
        result = integrator(fct, -1.0, 2.0)
        benchmark = 1.74999999998
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_004_gauss_legendre(self):
        fct = lambda x: x * x
        integrator = gauss_legendre()
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.583333333327
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_005_gauss_legendre(self):
        fct = lambda x: x * x
        integrator = gauss_legendre()
        result = integrator(fct, -100.0, 99.0)
        benchmark = 116.083333332
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_006_gauss_legendre(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_legendre()
        result = integrator(fct, -1.0, 2.0)
        benchmark = 1.97620410004
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_007_gauss_legendre(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_legendre()
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.658734700012
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_008_gauss_legendre(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_legendre()
        result = integrator(fct, -100.0, 99.0)
        benchmark = 131.088205302
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_009_gauss_legendre(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_legendre()
        result = integrator(fct, -1.0, 2.0)
        benchmark = -2.43433980503
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_010_gauss_legendre(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_legendre()
        result = integrator(fct, 0.0, 1.0)
        benchmark = -0.811446601677
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_011_gauss_legendre(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_legendre()
        result = integrator(fct, -100.0, 99.0)
        benchmark = -497.499999995
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_012_gauss_lobatto(self):
        fct = lambda x: 2
        integrator = gauss_lobatto()
        result = integrator(fct, -1.0, 2.0)
        benchmark = 6.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_013_gauss_lobatto(self):
        fct = lambda x: 2
        integrator = gauss_lobatto()
        result = integrator(fct, 0.0, 1.0)
        benchmark = 2.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_014_gauss_lobatto(self):
        fct = lambda x: 2
        integrator = gauss_lobatto()
        result = integrator(fct, -100.0, 99.0)
        benchmark = 398.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_015_gauss_lobatto(self):
        fct = lambda x: x * x
        integrator = gauss_lobatto()
        result = integrator(fct, -1.0, 2.0)
        benchmark = 3.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_016_gauss_lobatto(self):
        fct = lambda x: x * x
        integrator = gauss_lobatto()
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.333333333333
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_017_gauss_lobatto(self):
        fct = lambda x: x * x
        integrator = gauss_lobatto()
        result = integrator(fct, -100.0, 99.0)
        benchmark = 656766.3333333333
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_018_gauss_lobatto(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_lobatto()
        result = integrator(fct, -1.0, 2.0)
        benchmark = 1.62890552357
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_019_gauss_lobatto(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_lobatto()
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.746824132812
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_020_gauss_lobatto(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_lobatto()
        result = integrator(fct, -100.0, 99.0)
        benchmark = 1.77245385091
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_021_gauss_lobatto(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_lobatto()
        result = integrator(fct, -1.0, 2.0)
        benchmark = -0.25
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_022_gauss_lobatto(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_lobatto()
        result = integrator(fct, 0.0, 1.0)
        benchmark = -1.5
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_023_gauss_lobatto(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_lobatto()
        result = integrator(fct, -100.0, 99.0)
        benchmark = 24009698.5
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_024_simplex_steps_1000(self):
        fct = lambda x: 2
        integrator = simplex(steps=1000)
        result = integrator(fct, -1.0, 2.0)
        benchmark = 6.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_025_simplex_steps_1000(self):
        fct = lambda x: 2
        integrator = simplex(steps=1000)
        result = integrator(fct, 0.0, 1.0)
        benchmark = 2.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_026_simplex_steps_1000(self):
        fct = lambda x: 2
        integrator = simplex(steps=1000)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 398.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_027_simplex_steps_1000(self):
        fct = lambda x: x * x
        integrator = simplex(steps=1000)
        result = integrator(fct, -1.0, 2.0)
        benchmark = 3.0000045
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_028_simplex_steps_1000(self):
        fct = lambda x: x * x
        integrator = simplex(steps=1000)
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.3333335
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_029_simplex_steps_1000(self):
        fct = lambda x: x * x
        integrator = simplex(steps=1000)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 656767.6467664994
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_030_simplex_steps_1000(self):
        fct = lambda x: exp(-x * x)
        integrator = simplex(steps=1000)
        result = integrator(fct, -1.0, 2.0)
        benchmark = 1.62890491681
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_031_simplex_steps_1000(self):
        fct = lambda x: exp(-x * x)
        integrator = simplex(steps=1000)
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.746824071499
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_032_simplex_steps_1000(self):
        fct = lambda x: exp(-x * x)
        integrator = simplex(steps=1000)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 1.77245385091
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_033_simplex_steps_1000(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = simplex(steps=1000)
        result = integrator(fct, -1.0, 2.0)
        benchmark = -0.248991251001
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_034_simplex_steps_1000(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = simplex(steps=1000)
        result = integrator(fct, 0.0, 1.0)
        benchmark = -1.5
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_035_simplex_steps_1000(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = simplex(steps=1000)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 24009795.547195956
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_036_simplex(self):
        fct = lambda x: 2
        integrator = simplex()
        result = integrator(fct, -1.0, 2.0)
        benchmark = 6.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_037_simplex(self):
        fct = lambda x: 2
        integrator = simplex()
        result = integrator(fct, 0.0, 1.0)
        benchmark = 2.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_038_simplex(self):
        fct = lambda x: 2
        integrator = simplex()
        result = integrator(fct, -100.0, 99.0)
        benchmark = 398.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_039_simplex(self):
        fct = lambda x: x * x
        integrator = simplex()
        result = integrator(fct, -1.0, 2.0)
        benchmark = 3.00045
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_040_simplex(self):
        fct = lambda x: x * x
        integrator = simplex()
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.33335
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_041_simplex(self):
        fct = lambda x: x * x
        integrator = simplex()
        result = integrator(fct, -100.0, 99.0)
        benchmark = 656897.67665
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_042_simplex(self):
        fct = lambda x: exp(-x * x)
        integrator = simplex()
        result = integrator(fct, -1.0, 2.0)
        benchmark = 1.62884484614
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_043_simplex(self):
        fct = lambda x: exp(-x * x)
        integrator = simplex()
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.746818001468
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_044_simplex(self):
        fct = lambda x: exp(-x * x)
        integrator = simplex()
        result = integrator(fct, -100.0, 99.0)
        benchmark = 1.76997318866
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_045_simplex(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = simplex()
        result = integrator(fct, -1.0, 2.0)
        benchmark = -0.23912601
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_046_simplex(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = simplex()
        result = integrator(fct, 0.0, 1.0)
        benchmark = -1.5
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_047_simplex(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = simplex()
        result = integrator(fct, -100.0, 99.0)
        benchmark = 24019401.98376875
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_048_gauss_kronrod(self):
        fct = lambda x: 2
        integrator = gauss_kronrod()
        result = integrator(fct, -1.0, 2.0)
        benchmark = 6.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_049_gauss_kronrod(self):
        fct = lambda x: 2
        integrator = gauss_kronrod()
        result = integrator(fct, 0.0, 1.0)
        benchmark = 2.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_050_gauss_kronrod(self):
        fct = lambda x: 2
        integrator = gauss_kronrod()
        result = integrator(fct, -100.0, 99.0)
        benchmark = 398.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_051_gauss_kronrod(self):
        fct = lambda x: x * x
        integrator = gauss_kronrod()
        result = integrator(fct, -1.0, 2.0)
        benchmark = 3.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_052_gauss_kronrod(self):
        fct = lambda x: x * x
        integrator = gauss_kronrod()
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.333333333333
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_053_gauss_kronrod(self):
        fct = lambda x: x * x
        integrator = gauss_kronrod()
        result = integrator(fct, -100.0, 99.0)
        benchmark = 656766.3333333333
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_054_gauss_kronrod(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_kronrod()
        result = integrator(fct, -1.0, 2.0)
        benchmark = 1.62890552357
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_055_gauss_kronrod(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_kronrod()
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.746824132812
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_056_gauss_kronrod(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_kronrod()
        result = integrator(fct, -100.0, 99.0)
        benchmark = 1.7724538509055159
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_057_gauss_kronrod(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_kronrod()
        result = integrator(fct, -1.0, 2.0)
        benchmark = -0.263211802191
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_058_gauss_kronrod(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_kronrod()
        result = integrator(fct, 0.0, 1.0)
        benchmark = -1.5
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_059_gauss_kronrod(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_kronrod()
        result = integrator(fct, -100.0, 99.0)
        benchmark = 24009698.44306267
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_060_gauss_legendre_steps_500(self):
        fct = lambda x: 2
        integrator = gauss_legendre(steps=500)
        result = integrator(fct, -1.0, 2.0)
        benchmark = 5.99999999956
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_061_gauss_legendre_steps_500(self):
        fct = lambda x: 2
        integrator = gauss_legendre(steps=500)
        result = integrator(fct, 0.0, 1.0)
        benchmark = 1.99999999985
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_062_gauss_legendre_steps_500(self):
        fct = lambda x: 2
        integrator = gauss_legendre(steps=500)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 397.99999997
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_063_gauss_legendre_steps_500(self):
        fct = lambda x: x * x
        integrator = gauss_legendre(steps=500)
        result = integrator(fct, -1.0, 2.0)
        benchmark = 1.74999999973
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_064_gauss_legendre_steps_500(self):
        fct = lambda x: x * x
        integrator = gauss_legendre(steps=500)
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.583333333242
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_065_gauss_legendre_steps_500(self):
        fct = lambda x: x * x
        integrator = gauss_legendre(steps=500)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 116.083333315
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_066_gauss_legendre_steps_500(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_legendre(steps=500)
        result = integrator(fct, -1.0, 2.0)
        benchmark = 1.97620409996
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_067_gauss_legendre_steps_500(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_legendre(steps=500)
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.658734699986
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_068_gauss_legendre_steps_500(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_legendre(steps=500)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 131.088205297
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_069_gauss_legendre_steps_500(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_legendre(steps=500)
        result = integrator(fct, -1.0, 2.0)
        benchmark = -2.40726813703
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_070_gauss_legendre_steps_500(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_legendre(steps=500)
        result = integrator(fct, 0.0, 1.0)
        benchmark = -0.802422712344
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_071_gauss_legendre_steps_500(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_legendre(steps=500)
        result = integrator(fct, -100.0, 99.0)
        benchmark = -497.499999963
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_072_gauss_kronrod_check_abs_tolerance_check_rel_tolerance(self):
        fct = lambda x: 2
        integrator = gauss_kronrod(check_abs_tolerance=True, check_rel_tolerance=True)
        result = integrator(fct, -1.0, 2.0)
        benchmark = 6.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_073_gauss_kronrod_check_abs_tolerance_check_rel_tolerance(self):
        fct = lambda x: 2
        integrator = gauss_kronrod(check_abs_tolerance=True, check_rel_tolerance=True)
        result = integrator(fct, 0.0, 1.0)
        benchmark = 2.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_074_gauss_kronrod_check_abs_tolerance_check_rel_tolerance(self):
        fct = lambda x: 2
        integrator = gauss_kronrod(check_abs_tolerance=True, check_rel_tolerance=True)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 398.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_075_gauss_kronrod_check_abs_tolerance_check_rel_tolerance(self):
        fct = lambda x: x * x
        integrator = gauss_kronrod(check_abs_tolerance=True, check_rel_tolerance=True)
        result = integrator(fct, -1.0, 2.0)
        benchmark = 3.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_076_gauss_kronrod_check_abs_tolerance_check_rel_tolerance(self):
        fct = lambda x: x * x
        integrator = gauss_kronrod(check_abs_tolerance=True, check_rel_tolerance=True)
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.333333333333
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_077_gauss_kronrod_check_abs_tolerance_check_rel_tolerance(self):
        fct = lambda x: x * x
        integrator = gauss_kronrod(check_abs_tolerance=True, check_rel_tolerance=True)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 656766.3333333333
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_078_gauss_kronrod_check_abs_tolerance_check_rel_tolerance(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_kronrod(check_abs_tolerance=True, check_rel_tolerance=True)
        result = integrator(fct, -1.0, 2.0)
        benchmark = 1.62890552357
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_079_gauss_kronrod_check_abs_tolerance_check_rel_tolerance(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_kronrod(check_abs_tolerance=True, check_rel_tolerance=True)
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.746824132812
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_080_gauss_kronrod_check_abs_tolerance_check_rel_tolerance(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_kronrod(check_abs_tolerance=True, check_rel_tolerance=True)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 1.7724538509055159
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_081_gauss_kronrod_check_abs_tolerance_check_rel_tolerance(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_kronrod(check_abs_tolerance=True, check_rel_tolerance=True)
        result = integrator(fct, -1.0, 2.0)
        benchmark = -0.263211802191
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_082_gauss_kronrod_check_abs_tolerance_check_rel_tolerance(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_kronrod(check_abs_tolerance=True, check_rel_tolerance=True)
        result = integrator(fct, 0.0, 1.0)
        benchmark = -1.5
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_083_gauss_kronrod_check_abs_tolerance_check_rel_tolerance(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_kronrod(check_abs_tolerance=True, check_rel_tolerance=True)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 24009698.44306267
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_084_gauss_lobatto_max_iter_127(self):
        fct = lambda x: 2
        integrator = gauss_lobatto(max_number_of_iterations=255, abs_tolerance=1.0e-7)
        result = integrator(fct, -1.0, 2.0)
        benchmark = 6.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_085_gauss_lobatto_max_iter_127(self):
        fct = lambda x: 2
        integrator = gauss_lobatto(max_number_of_iterations=255, abs_tolerance=1.0e-7)
        result = integrator(fct, 0.0, 1.0)
        benchmark = 2.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_086_gauss_lobatto_max_iter_127(self):
        fct = lambda x: 2
        integrator = gauss_lobatto(max_number_of_iterations=255, abs_tolerance=1.0e-7)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 398.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_087_gauss_lobatto_max_iter_127(self):
        fct = lambda x: x * x
        integrator = gauss_lobatto(max_number_of_iterations=255, abs_tolerance=1.0e-7)
        result = integrator(fct, -1.0, 2.0)
        benchmark = 3.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_088_gauss_lobatto_max_iter_127(self):
        fct = lambda x: x * x
        integrator = gauss_lobatto(max_number_of_iterations=255, abs_tolerance=1.0e-7)
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.333333333333
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_089_gauss_lobatto_max_iter_127(self):
        fct = lambda x: x * x
        integrator = gauss_lobatto(max_number_of_iterations=255, abs_tolerance=1.0e-7)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 656766.3333333333
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_090_gauss_lobatto_max_iter_127(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_lobatto(max_number_of_iterations=255, abs_tolerance=1.0e-7)
        result = integrator(fct, -1.0, 2.0)
        benchmark = 1.62890552357
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_091_gauss_lobatto_max_iter_127(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_lobatto(max_number_of_iterations=255, abs_tolerance=1.0e-7)
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.746824132812
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_092_gauss_lobatto_max_iter_127(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_lobatto(max_number_of_iterations=255, abs_tolerance=1.0e-7)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 1.77245385091
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_093_gauss_lobatto_max_iter_127(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_lobatto(max_number_of_iterations=255, abs_tolerance=1.0e-7)
        result = integrator(fct, -1.0, 2.0)
        benchmark = -0.250000000002
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_094_gauss_lobatto_max_iter_127(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_lobatto(max_number_of_iterations=255, abs_tolerance=1.0e-7)
        result = integrator(fct, 0.0, 1.0)
        benchmark = -1.5
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_095_gauss_lobatto_max_iter_127(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_lobatto(max_number_of_iterations=255, abs_tolerance=1.0e-7)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 24009698.499997977
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_096_gauss_kronrod_check_rel_tolerance(self):
        fct = lambda x: 2
        integrator = gauss_kronrod(check_abs_tolerance=False, check_rel_tolerance=True)
        result = integrator(fct, -1.0, 2.0)
        benchmark = 6.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_097_gauss_kronrod_check_rel_tolerance(self):
        fct = lambda x: 2
        integrator = gauss_kronrod(check_abs_tolerance=False, check_rel_tolerance=True)
        result = integrator(fct, 0.0, 1.0)
        benchmark = 2.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_098_gauss_kronrod_check_rel_tolerance(self):
        fct = lambda x: 2
        integrator = gauss_kronrod(check_abs_tolerance=False, check_rel_tolerance=True)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 398.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_099_gauss_kronrod_check_rel_tolerance(self):
        fct = lambda x: x * x
        integrator = gauss_kronrod(check_abs_tolerance=False, check_rel_tolerance=True)
        result = integrator(fct, -1.0, 2.0)
        benchmark = 3.0
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_100_gauss_kronrod_check_rel_tolerance(self):
        fct = lambda x: x * x
        integrator = gauss_kronrod(check_abs_tolerance=False, check_rel_tolerance=True)
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.333333333333
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_101_gauss_kronrod_check_rel_tolerance(self):
        fct = lambda x: x * x
        integrator = gauss_kronrod(check_abs_tolerance=False, check_rel_tolerance=True)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 656766.3333333333
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_102_gauss_kronrod_check_rel_tolerance(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_kronrod(check_abs_tolerance=False, check_rel_tolerance=True)
        result = integrator(fct, -1.0, 2.0)
        benchmark = 1.62890552357
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_103_gauss_kronrod_check_rel_tolerance(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_kronrod(check_abs_tolerance=False, check_rel_tolerance=True)
        result = integrator(fct, 0.0, 1.0)
        benchmark = 0.746824132812
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_104_gauss_kronrod_check_rel_tolerance(self):
        fct = lambda x: exp(-x * x)
        integrator = gauss_kronrod(check_abs_tolerance=False, check_rel_tolerance=True)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 1.7724538509055159
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_105_gauss_kronrod_check_rel_tolerance(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_kronrod(check_abs_tolerance=False, check_rel_tolerance=True)
        result = integrator(fct, -1.0, 2.0)
        benchmark = -0.263211802191
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_106_gauss_kronrod_check_rel_tolerance(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_kronrod(check_abs_tolerance=False, check_rel_tolerance=True)
        result = integrator(fct, 0.0, 1.0)
        benchmark = -1.5
        self.assertAlmostEqual(benchmark, result, 8)

    def test_integrator_107_gauss_kronrod_check_rel_tolerance(self):
        fct = lambda x: x * x * x if x > 1 else x - 2
        integrator = gauss_kronrod(check_abs_tolerance=False, check_rel_tolerance=True)
        result = integrator(fct, -100.0, 99.0)
        benchmark = 24009698.44306267
        self.assertAlmostEqual(benchmark, result, 8)

    # ----------------------- END: INTEGRATION TEST ------------------------------

    # ----------------------- OPTIMIZER TEST ------------------------------
    def _init_polynom(self):
        a, b, c, d, e = 1, 4, -6, -6, 1
        return lambda x: a * x * x * x * x + b * x * x * x + c * x * x + d * x + e

    def test_minimize_algorithm_1dim_brent_1(self):
        fct = self._init_polynom()
        result = brent(fct, 0.0, 1.0, 4.0)
        benchmark = (1.0772836395652352, -6.079165700291461)
        self._assertEqual(benchmark, result)

    def test_minimize_algorithm_1dim_golden_1(self):
        fct = self._init_polynom()
        result = golden(fct, 0.0, 1.0, 4.0)
        benchmark = (1.077283631638824, -6.07916570029146)
        self._assertEqual(benchmark, result)

    def test_minimize_algorithm_1dim_brent_scaled(self):
        constraint = Constraint(0.0, 4.0)
        t = TangentsTransformation(constraint)
        tinv = TangentsInverseTransformation(constraint)
        p = self._init_polynom()
        fct = CompositionFct(p, tinv)
        result_scaled = brent(fct, t(0.1), t(1.0), t(3.9))
        benchmark_rescaled = (-0.8854173749579757, -6.079165700291461)
        result = (tinv(result_scaled[0]), result_scaled[1])
        benchmark = (1.0772836393669956, -6.079165700291461)
        self._assertEqual(benchmark_rescaled, result_scaled)
        self._assertEqual(benchmark, result)

    def test_optimizer_1dim_brent_0(self):
        fct = self._init_polynom()
        opt = Optimizer1Dim(minimize_algorithm=brent)
        result = []
        result.append(opt.optimize(fct, Constraint(0.0, 2.0), 1.0))
        result.append(opt.optimize(fct, Constraint(0.0, 2.7), 1.0))
        result.append(opt.optimize(fct, Constraint(0.0, 4.2), 1.0))
        benchmark = []
        benchmark.append(OptimizerResult.create_succesful(1.07728364364, -6.07916570029, 32))
        benchmark.append(OptimizerResult.create_succesful(1.07728363789, -6.07916570029, 40))
        benchmark.append(OptimizerResult.create_succesful(1.07728363067, -6.07916570029, 50))
        for i in xrange(3):
            self._assert_optimizer_results(benchmark[i], result[i], 7)

    def test_optimizer_1dim_golden_0(self):
        fct = self._init_polynom()
        opt = Optimizer1Dim(minimize_algorithm=golden)
        result = []
        result.append(opt.optimize(fct, Constraint(0.0, 2.0), 1.0))
        result.append(opt.optimize(fct, Constraint(0.0, 2.7), 1.0))
        result.append(opt.optimize(fct, Constraint(0.0, 4.2), 1.0))

        benchmark = []
        benchmark.append(OptimizerResult.create_succesful(1.0, -6.0, 6))
        benchmark.append(OptimizerResult.create_succesful(1.0, -6.0, 80))
        benchmark.append(OptimizerResult.create_succesful(1.0, -6.0, 80))
        for i in xrange(3):
            self._assert_optimizer_results(benchmark[i], result[i])

    def test_optimizer_1dim_brent_1(self):
        fct = self._init_polynom()
        opt = Optimizer1Dim(minimize_algorithm=brent)
        result = opt.optimize(fct, Constraint(-10.0, -2.0), 1.0)
        benchmark = OptimizerResult.create_succesful(-3.70107061641, -74.1359364077, 40)
        self._assert_optimizer_results(benchmark, result)

    def test_optimizer_1dim_brent_2(self):
        fct = lambda x: x * (x - PI) * (x - PI)
        constraint = Constraint(0.0, 5.0)
        opt = Optimizer1Dim(minimize_algorithm=brent)
        result = opt.optimize(fct, constraint, 1.0)
        benchmark = OptimizerResult.create_succesful(3.14159265057, 2.87208663251e-17, 43)
        self._assert_optimizer_results(benchmark, result)

    def test_tangents_invers_tangents_transformation(self):
        constraint = Constraint(0.0, 5.0)
        t = TangentsTransformation(constraint)
        tinv = TangentsInverseTransformation(constraint)
        values = [-4.2, -2.03, -1.0, 0.0, 1.0, 2.3, 4.5, 1001.01]
        for x in values:
            y = t(tinv(x))
            self.assertAlmostEqual(x, y, 8)

    def test_tangents_tangents_invers_transformation(self):
        constraint = Constraint(-30.0, 1002.0)
        t = TangentsTransformation(constraint)
        tinv = TangentsInverseTransformation(constraint)
        values = [-4.2, -2.03, -1.0, 0.0, 1.0, 2.3, 4.5, 1001.01]
        for x in values:
            z = tinv(t(x))
            self.assertAlmostEqual(x, z, 8)

    def test_minimum_bracketing_0(self):
        fct = lambda x: (x + 1) * (x + 1)
        benchmark = (-0.23606798000000007, -1.0, -1.4721359544093597)
        result = minimum_bracketing(fct, 1.0, 2.0)
        self._assertEqual(benchmark, result)

    def test_minimum_bracketing_1(self):
        fct = lambda x: exp(x) * (x + 1) * (x + 1)
        benchmark = (0.0, -1.23606798, -2.0000000055906404)
        result = minimum_bracketing(fct, 0.0, 2.0)
        self._assertEqual(benchmark, result)

    def test_minimum_bracketing_2(self):
        fct = lambda x: exp(x) * (x + 1) * (x + 1)
        benchmark = (1.0, -1.0, -2.23606798)
        result = minimum_bracketing(fct, -1.0, 2.0)
        self._assertEqual(benchmark, result)

    def test_mn_brak(self):
        fct = self._init_polynom()
        result = mn_brak(0.0, 5.0, fct)
        benchmark = (0.0, -3.09016995, -5.0000000139766, 1.0, -64.60159985371774, 6.000002040583652)
        self._assertEqual(benchmark, result, 8)

    def test_minimum_bracketing_scaled(self):
        constraint = Constraint(0.0, 5.0)
        t = TangentsTransformation(constraint)
        p = self._init_polynom()
        fct = CompositionFct(p, t)
        result = mn_brak(0.1, 1.0, fct)
        benchmark = (0.1, 1.0, 1.556230591, 46343.60499652936, -8.949238582537712, 1.3006670200315953)
        self._assertEqual(benchmark, result, 7)

    def test_composion_fct(self):
        compo_fct = CompositionFct(lambda x: x * x, lambda x: x + 5)
        y = compo_fct(2)
        self.assertEqual(y, 49)

    def test_roots_of_cubic_polynom_3real(self):
        roots = roots_of_cubic_polynom(a1=1, a2=-1, a3=0)
        self.assertAlmostEqual(roots[0].real, -1.6180339887498947)
        self.assertAlmostEqual(roots[0].imag, 0.0)
        self.assertAlmostEqual(roots[1].real, 0.6180339887498947)
        self.assertAlmostEqual(roots[1].imag, 0.0)
        self.assertAlmostEqual(roots[2].real, 0.0)
        self.assertAlmostEqual(roots[2].imag, 0.0)

    def test_roots_of_cubic_polynom_1real_2imag(self):
        roots = roots_of_cubic_polynom(a1=1, a2=-1, a3=1)
        self.assertAlmostEqual(roots[0].real, -1.839286755214161)
        self.assertAlmostEqual(roots[0].imag, 0.0)
        self.assertAlmostEqual(roots[1].real, 0.41964337760708054)
        self.assertAlmostEqual(roots[1].imag, 1.7320508075688772)
        self.assertAlmostEqual(roots[2].real, 0.41964337760708054)
        self.assertAlmostEqual(roots[2].imag, -1.7320508075688772)

    def _assert_optimizer_results(self, result, benchmark, places=8):
        self.assertAlmostEqual(result.xmin, benchmark.xmin, places,
                               "Optimizer result, xmin not equal. " + self._get_not_equal_str(result.xmin,
                                                                                              benchmark.xmin))
        self.assertAlmostEqual(result.fmin, benchmark.fmin, places,
                               "Optimizer result, fmin not equal. " + self._get_not_equal_str(result.fmin,
                                                                                              benchmark.fmin))
        # self.assertEqual(result.number_of_function_calls, benchmark.number_of_function_calls, "Optimizer result, number_of_function_calls not equal. " + self._get_not_equal_str(result.number_of_function_calls, benchmark.number_of_function_calls))
        self.assertEqual(result.successful, benchmark.successful,
                         "Optimizer result, successful not equal. " + self._get_not_equal_str(result.successful,
                                                                                              benchmark.successful))
        self.assertEqual(result.error_msg, benchmark.error_msg,
                         "Optimizer result, error_msg not equal. " + self._get_not_equal_str(result.error_msg,
                                                                                             benchmark.error_msg))

    # ----------------------- END: OPTIMIZER TEST ------------------------------
    # ----------------------- NORMAL DISTRIBUTION TEST -------------------------
    def test_compare_integral_of_density_with_cdf(self):
        fct = density_normal_dist
        integrator = gauss_kronrod(min_number_of_iterations=15)
        l_bound = -1000.0
        x_values = [-10.0, -1.3, -0.5, 0.0, 1.3, 5.0, 100.0, 1000.0]
        for x in x_values:
            integral = integrator(fct, l_bound, x)
            cdf_value = cdf_abramowitz_stegun(x)
            self.assertAlmostEqual(integral, cdf_value, 4)

    # ----------------------- END: NORMAL DISTRIBUTION TEST --------------------



    def _get_not_equal_str(self, x, y):
        return str(x) + " != " + str(y)

    def _assertEqual(self, benchmark, result, places=None):
        i = 0
        for b, r in zip(benchmark, result):
            msg = "The " + str(i) + "-th Benchmark value " + str(b) + " is not equal to the result " + str(r)
            if places is None:
                self.assertEqual(b, r, msg)
            else:
                self.assertAlmostEqual(b, r, places, msg)
            i = i + 1


class SurfaceTest(unittest.TestCase):

    def test_nested(self):
        xaxis = [float(x) for x in range(100)]
        yaxis = [float(y) for y in range(20)]
        values = [[x*y for y in yaxis] for x in xaxis]
        surface = Surface(xaxis, yaxis, values)
        for x in xaxis:
            for y in yaxis:
                self.assertAlmostEqual(surface(x, y), x*y)

if __name__ == "__main__":
    import sys
    import os
    from datetime import datetime

    start_time = datetime.now()

    print('')
    print('======================================================================')
    print('')
    print('run %s' % __file__)
    print('in %s' % os.getcwd())
    print('started  at %s' % str(start_time))
    print('')
    print('----------------------------------------------------------------------')
    print('')

    suite = unittest.TestLoader().loadTestsFromModule(__import__("__main__"))
    testrunner = unittest.TextTestRunner(stream=sys.stdout, descriptions=2, verbosity=2)
    testrunner.run(suite)

    print('')
    print('======================================================================')
    print('')
    print('ran %s' % __file__)
    print('in %s' % os.getcwd())
    print('started  at %s' % str(start_time))
    print('finished at %s' % str(datetime.now()))
    print('')
    print('----------------------------------------------------------------------')
    print('')


