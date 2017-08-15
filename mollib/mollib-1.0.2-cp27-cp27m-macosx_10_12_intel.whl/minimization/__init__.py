"""
Minimizer objects are used to minimize functions like chi^2 and RMSDs. These
can be run in parallel for minimization algorithms that depend on randomized
input by setting the ``no_runs`` attribute to a number.

In the following example, the Basin Hoping minimizer
(:obj:`mollib.minimization.BHMinimizer`) is used to find the ``a`` and ``b``
parameters for a quadratic function. This function is minimized only once, and
only a single minimum result is returned. The results are named tuples with
a ``minimum`` and a minimized ``parameters`` list.

Examples
--------
>>> import numpy as np
>>> from mollib.minimization import BHMinimizer, MinimizerParameter
>>> msd = lambda y_expt, x, a, b: sum(((a * x ** 2 + b) - y_expt)**2)
>>> x = np.arange(0, 10, 1)     # the x-points
>>> y_expt = 3.2 * x **2 - 2.5  # the simulated 'experimental' y-points
>>> m = BHMinimizer()           # Create the minimizer
>>> m.function = msd            # Set the function to minimize
>>> m.no_runs = None            # Set to only run the minimization once
>>> m.add_parameters(y_expt)    # Add parameters to be passed to min.function
>>> m.add_parameters(x)         # Parameters passed to function in order added
>>> m.add_parameters(MinimizerParameter(name='a', value=1.0,
...                                     range=(-4.0, 4.0)))
>>> m.add_parameters(MinimizerParameter(name='b', value=1.0,
...                                     range=(-4.0, 4.0)))
>>> results = m.minimize()      # Run the minimization
>>> best_result = results[0]
>>> print("minimum = {:.3f}".format(best_result.minimum))
minimum = 0.000
>>> for parameter in best_result.parameters:
...     print("{} = {:.1f}".format(parameter.name, parameter.value))
a = 3.2
b = -2.5
"""
from .minimizer import MinimizerParameter, Minimizer
from .montecarlo import MCMinimizer
from .basinhopping import BHMinimizer
from .gridrandom import GridRandomMinimizer
