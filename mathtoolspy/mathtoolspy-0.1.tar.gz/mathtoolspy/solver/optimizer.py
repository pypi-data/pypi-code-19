# -*- coding: utf-8 -*-

#  mathtoolspy
#  ------------
#  A fast, efficient Python library for mathematically operations, like
#  integration, solver, distributions and other useful functions.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/businessdate
#  License: APACHE Version 2 License (see LICENSE file)


from math import tan, atan, fabs

from mathtoolspy.utils.mathconst import PI, DOUBLE_TOL
from minimum_bracketing import minimum_bracketing

MAX_NUMBER_OF_FUNCTION_CALLS = 5000


class FctWithCount(object):
    def __init__(self, fct):
        self.fct = fct
        self.number_of_calls = 0

    def __call__(self, x):
        self.number_of_calls += 1
        return self.fct(x)


class DeviationFct(object):
    def __init__(self, fct, rescale=None, max_number_of_function_calls=MAX_NUMBER_OF_FUNCTION_CALLS):
        self._rescale = rescale if not rescale is None else lambda x: x
        self.fct = fct
        self.max_number_of_function_calls = max_number_of_function_calls

    def can_be_called(self):
        if self.fct.number_of_calls < self.max_number_of_function_calls:
            return True
        else:
            return False

    def __call__(self, value_t_scaled):
        # rescalling
        x = self._rescale(value_t_scaled)
        return self.fct(x)


class Constraint(object):
    def __init__(self, lower_bound, upper_bound):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def is_a_number(self):
        return fabs(self.upper_bound - self.lower_bound) < DOUBLE_TOL

    def mid_point(self):
        return (self.upper_bound + self.lower_bound) / 2.0

    def contains(self, x):
        return self.lower_bound <= x and self.upper_bound >= x

    def __str__(self):
        return "[" + str(self.lower_bound) + ", " + str(self.upper_bound) + "]"

    @staticmethod
    def create_constraint(constraint_tupel):
        ret = []
        for t in constraint_tupel:
            ret.append(Constraint(t[0], t[1]))
        return ret


class InfinityConstraint:
    def __init__(self):
        pass

    def is_a_number(self):
        return False

    def mid_point(self):
        return 0.0

    def contains(self, x):
        return True

    def __str__(self):
        return "]-infinity, infinity["


class Optimizer1Dim(object):
    def __init__(self, minimize_algorithm):
        self.minimize_algorithm = minimize_algorithm

    def _setup_transformations(self, constraint):
        if constraint is None:
            return lambda x: x, lambda x: x
        else:
            return TangentsTransformation(constraint), TangentsInverseTransformation(constraint)

    def _rescale(self, x):
        return self.tinv(x)

    def optimize(self, function, constraint=None, initial_value=0.0, tolerance=0.00000001):
        # Set the function with call count
        fct = FctWithCount(function)
        # Check if the upper and lower bound are equal.
        # In this case return the value of the bound as the solution.
        if not constraint is None and constraint.is_a_number():
            x = constraint.mid_point()
            fx = fct(x)
            n = fct.number_of_calls
            return OptimizerResult.create_succesful(x, fx, n)

        # set the t and tInv transformation.
        t, self.tinv = self._setup_transformations(constraint)
        dev_fct = DeviationFct(fct, self._rescale, MAX_NUMBER_OF_FUNCTION_CALLS)
        # Bracketing is useful for both methods implemented so far, namely 'GoldenSection' and 'Brent'.
        # The initial value has to be transformed, since the deviation function is transformed as well.
        mbr = minimum_bracketing(dev_fct, t(initial_value))
        if not mbr:
            return OptimizerResult.create_not_succesful("Minimum Bracketing failed.", fct.number_of_calls)
        a, b, c = mbr
        # The real minimization
        xmin_t, fmin = self.minimize_algorithm(dev_fct, a, b, c, tolerance)
        if xmin_t is None:
            return OptimizerResult.create_not_succesful("No minimum found.", fct.number_of_calls)
        # re-transform the pre-images:
        xmin = self._rescale(xmin_t)
        # return OptimizerResult.create_succesful(self.tinv(xmin_t), self.tinv(fmin_t), n_calls)
        return OptimizerResult.create_succesful(xmin, fmin, fct.number_of_calls)


class Optimizer(object):
    def __init__(self, minimizeAlgorithm):
        self.minimize_algorithm = minimizeAlgorithm

    def optimize(self, function, constraint, initialValues, tolerance=0.00000001):
        fct = Optimizer.fctWithCount(function)
        self._checkDimension(constraint, initialValues)
        self.tinvs = [TangentsInverseTransformation(c) if not c.is_a_number() else lambda x: x for c in constraint]
        transform = [TangentsTransformation(c) if not c.is_a_number() else lambda x: x for c in constraint]
        tInitialValue = [transform[i](initX) for i, initX in enumerate(initialValues)]
        devFct = DeviationFct(fct, self._rescale, MAX_NUMBER_OF_FUNCTION_CALLS)
        # try:
        minimizeResult = self.minimize_algorithm(devFct, tInitialValue, tolerance, MAX_NUMBER_OF_FUNCTION_CALLS)
        if minimizeResult[2]:
            rescaledX = self._rescale(minimizeResult[0])
            return OptimizerResult.create_succesful(rescaledX, minimizeResult[1], devFct.fct.number_of_calls)
        else:
            m1 = "Max number of function calls " + str(Optimizer.MAX_NUMBER_OF_FUNCTION_CALLS) + " exceeded."
            msg = m1 if devFct.fct.number_of_calls >= devFct.max_number_of_function_calls else "To many iterations."
            return OptimizerResult.create_not_succesful(msg, devFct.fct.number_of_calls)
            # except Exception as e:
            #   msg = str(e)
            #   return OptimizerNDimResult.create_not_succesful(msg, DevFct.fct.number_of_calls)

    def _rescale(self, t_scaled_value):
        return [self._tinvs[i](v) for i, v in enumerate(t_scaled_value)]

    def _checkDimension(self, constraint, initialValues):
        c = len(constraint) if constraint     else -1
        n = len(initialValues) if initialValues  else -1
        if n > -1 and c > -1:
            if n != c:
                raise Exception("Optimizer not correct initialized. Constraint dimension " +
                                str(c) + " and initial value dimension " + str(n) + " are not equal.")
            return n
        elif n > -1:
            return n
        elif c > -1:
            return c
        else:
            raise Exception("Optimizer not initialized. Missing constraint and/or initial values.")


class OptimizerResult(object):
    def __init__(self):
        self.xmin = None
        self.fmin = None
        self.error_msg = None
        self.successful = False
        self.number_of_function_calls = -1

    @staticmethod
    def create_succesful(xmin, fmin, numberOfFunctionCalls):
        ret = OptimizerResult()
        ret.xmin = xmin
        ret.fmin = fmin
        ret.successful = True
        ret.number_of_function_calls = numberOfFunctionCalls
        return ret

    @staticmethod
    def create_not_succesful(errorMsg, numberOfFunctionCalls):
        ret = OptimizerResult()
        ret.error_msg = errorMsg
        ret.successful = False
        ret.number_of_function_calls = numberOfFunctionCalls
        return ret

    def __str__(self):
        if self.successful:
            return str(("xmin = " + str(self.xmin), "fmin = " + str(self.fmin),
                        "fct_calls = " + str(self.number_of_function_calls)))
        else:
            return str(("err_msg = " + self.error_msg, "fct_calls = " + str(self.number_of_function_calls)))


class TangentsInverseTransformation(object):
    def __init__(self, constraint):
        self.a = constraint.lower_bound
        self.d = constraint.upper_bound - self.a

    def __call__(self, x):
        return self.a + self.d * (0.5 + atan(x) / PI)


class TangentsTransformation(object):
    def __init__(self, constraint):
        self.a = constraint.lower_bound
        self.d = constraint.upper_bound - self.a

    def __call__(self, x):
        return tan(((x - self.a) / self.d - 0.5) * PI)


class OptimizerInitialValuesSearchOnFixedGrid(object):
    """
    An optimizer, which searches in a fix grid for the best initial value.
    """

    def __init__(self, minimizeAlgorithm, stepsPerAxis):
        self.optimizer = Optimizer(minimizeAlgorithm)
        self.stepsPerAxis = stepsPerAxis

    def optimize(self, function, constraint, initialValues, tolerance=0.00000001):
        r = self.optimizer.optimize(function, constraint, initialValues, tolerance)
        if r.successful:
            return r

        fc = Optimizer.fctWithCount(function)
        bestInitial = self._findBestInitialValue(fc, constraint)
        ret = self.optimizer.optimize(function, constraint, bestInitial, tolerance)
        ret.number_of_function_calls = ret.number_of_function_calls + r.number_of_function_calls + fc.number_of_calls
        return ret

    def _findBestInitialValue(self, function, constraint):
        grids = [self._getGrid(c, self.stepsPerAxis) for c in constraint]
        bestN = OptimizerInitialValuesSearchOnFixedGrid._bestNOf(1, lambda x, y: -1 if x < y else 1 if x > y else 0)
        for x in combinations(grids):
            bestN.add(x, function(x))
        return bestN.values[0][0]

    class _bestNOf:
        def __init__(self, n, compare):
            '''
            A compare methods: compare(x, y). -1 if x is better, 0 if x equals y and 1 if y is better
            '''
            self.n = n
            self.values = [(None, None) for _ in range(self.n)]
            self._compare = compare

        def add(self, x, value):
            for i in range(self.n):
                v = self.values[i][1]
                k = self._compare(v, value) if v != None else 1
                if k == 1:
                    for j in range(self.n - 1, i, -1):
                        self.values[j] = self.values[j - 1]
                    self.values[i] = (x, value)

    def _getGrid(self, constraint, nSteps):
        a = constraint.lower_bound
        step = (constraint.upper_bound - a) / (nSteps + 2)
        return [a + i * step for i in range(1, nSteps + 1)]


class combinations:
    def __init__(self, listOfTupel):
        self.listOfTupel = listOfTupel
        self.m = len(listOfTupel)
        self.n = self._getDimensions()
        self.idx = [0 for _ in range(self.m)]  # counts the entires in a tupel
        self.stop = False if self.m > 0 else True

    def _getDimensions(self):
        n = []
        for x in self.listOfTupel:
            n.append(len(x))
        return n

    def __iter__(self):
        return self

    def __next__(self):
        if self.stop:
            raise StopIteration()
        x = self.listOfTupel
        ret = [x[i][j] for i, j in enumerate(self.idx)]
        self._increase(0)
        return ret

    def next(self):
        return self.__next__()

    def _increase(self, c):
        if c >= self.m:
            self.stop = True
            return
        self.idx[c] = self.idx[c] + 1
        if self.idx[c] == self.n[c]:
            self._reset(c + 1)
            self._increase(c + 1)

    def _reset(self, c):
        for i in range(c):
            self.idx[i] = 0
