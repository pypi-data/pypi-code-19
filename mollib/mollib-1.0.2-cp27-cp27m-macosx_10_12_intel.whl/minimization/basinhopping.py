import numpy as np
import scipy.optimize

from .minimizer import Minimizer, MinimizerParameter
from .montecarlo import MCMinimizer
from . import settings


class BHMinimizer(Minimizer):
    """A minimizer that uses Basin Hoping.

    Attributes
    ----------

    """

    bh_minimizer_kwargs = None
    bh_niter_success = None
    result = None

    def __init__(self, *args, **kwargs):
        self.bh_minimizer_kwargs = settings.bh_minimizer_kwargs
        self.bh_niter_success = settings.bh_niter_success
        super(BHMinimizer, self).__init__(*args, **kwargs)

    def minimize_function(self):
        """Minimize the :meth:`function`.

        This minimization is conducted using a Basin Hoping algorithm.
        """
        # Get the parameters
        parameter_args = []
        parameter_args += [p.value for p in self.parameters
                           if isinstance(p, MinimizerParameter)]
        x0 = np.array(parameter_args)

        # Setup the minimization function. This needs to be reorganized
        # because the basin hoping minimization function expects an array of
        # adjustable parameters as the first parameter
        def func(x):
            # Copy new 'x' floating parameters to the MinimizationParameter
            # counter parts
            item = 0
            parameter_args = []
            for parameter in self.parameters:
                if isinstance(parameter, MinimizerParameter):
                    parameter.value = x[item]
                    item += 1
                    parameter_args.append(parameter.value)
                else:
                    parameter_args.append(parameter)
            return self.function(*parameter_args)

        # Setup and run the basin hopping minimization
        bh = scipy.optimize.basinhopping
        result = bh(func=func, x0=x0,
                    minimizer_kwargs=self.bh_minimizer_kwargs,
                    niter_success=self.bh_niter_success)

        # Update this object's attributes with the new minimum and minimized
        # parameters
        self.result = result
        self.minimum_value = result.fun

        item = 0
        for parameter in self.parameters:
            if isinstance(parameter, MinimizerParameter):
                parameter.value = result.x[item]
                item += 1


class MCBHMinimizer(MCMinimizer, BHMinimizer):
    """A minimizer that uses Monte Carlo sampling followed by Basin Hoping
    minimization.
    """

    def minimize_function(self):
        """Minimize the :meth:`function`.

        This minimization is conducted using Monte Carlo sampling followed by
        Basin Hoping minimization.
        """
        MCMinimizer.minimize_function(self)
        BHMinimizer.minimize_function(self)

