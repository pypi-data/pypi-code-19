import random

from .minimizer import MinimizerParameter, Minimizer
from . import settings


class MCMinimizer(Minimizer):
    """Minimizer that uses Monte Carlo sampling.

    Attributes
    ----------
    baseseed: int, optional
        The minimizer's id will be added to this baseseed in initialize the
        RNG for each procress.
    iterations: int, optional
        The number of Monte Carlo random samplings to conduct for the
        minimization.
    """

    baseseed = 0
    iterations = None
    rng_initialized = False

    def __init__(self, *args, **kwargs):
        self.iterations = kwargs.get('iterations',
                                     settings.iterations)
        self.baseseed = kwargs.get('baseseed',
                                   settings.baseseed)
        super(MCMinimizer, self).__init__(*args, **kwargs)

    def minimize_function(self):
        """Minimize the :meth:`function`.

        This minimization is conducted by Monte-Carlo sampling and returning
        the best result.
        """

        # Initialize the RNG, if needed. The baseseed is incremented so that
        # the next run produces a different set of values
        random.seed(self.baseseed + self.id)

        # Get the initial minimum
        minimum = None
        parameter_args = []
        parameter_args += [p.value if isinstance(p, MinimizerParameter) else p
                           for p in self.parameters]

        minimum = self.function(*parameter_args)

        self.minimum_value = minimum

        # Generate random numbers and test their minimums
        for iteration in range(self.iterations):

            # Randomize the MinimizationParameters and see if there is a better
            # minimum
            parameter_args = []
            for parameter in self.parameters:
                if not isinstance(parameter, MinimizerParameter):
                    parameter_args.append(parameter)
                    continue

                # Use range, if specified, to randomly generate the next
                # parameter value
                if isinstance(parameter.range, tuple):
                    parameter_args.append(random.uniform(*parameter.range))
                else:
                    parameter_args.append(random.uniform(0.,
                                                         parameter.value * 2.0))

            # Get the new minimum and see if it's better
            new_minimum = self.function(*parameter_args)

            if new_minimum < self.minimum_value:
                # If it is better, replace the new values in the parameters
                self.minimum_value = new_minimum

                for parameter, arg in zip(self.parameters, parameter_args):
                    if not isinstance(parameter, MinimizerParameter):
                        continue
                    parameter.value = arg

    def minimize(self):
        """Minimize and return the results.

        This is a wrapper to the parent minimize function that moves the seed
        forward by a defined amount so that subsequent runs of this minimization
        function returns different random numbers.
        """
        return_value = super(MCMinimizer, self).minimize()
        self.baseseed += 1000
        return return_value
