"""
Minimization class for a randomized grid sampler.
"""

from .minimizer import MinimizerParameter, Minimizer
from .generators import random_parameter_grid
from . import settings


class GridRandomMinimizer(Minimizer):
    """Minimizer that randomly samples a grid of the multidimensional parameter 
    space.

    Attributes
    ----------
    baseseed: int, optional
        The minimizer's id will be added to this baseseed in initialize the
        RNG for each procress.
    iterations: int, optional
        The number of Monte Carlo random samplings to conduct for the
        minimization.
    grid_size: int, optional
        
    """

    baseseed = 0
    iterations = None
    grid_size = None

    def __init__(self, iterations=None, grid_size=None, *args, **kwargs):
        self.iterations = (iterations if iterations is not None
                           else settings.iterations)
        self.grid_size = grid_size
        self.baseseed = kwargs.pop('baseseed',
                                   settings.baseseed)
        super(GridRandomMinimizer, self).__init__(*args, **kwargs)

    def minimize_function(self):
        """Minimize the :meth:`function`.

        This minimization is conducted by Grid Randomized sampling and returning
        the best result.
        """
        # Initialize the grid_size if it hasn't been specified
        if self.grid_size is None:
            no_adjust_params = len(self.adjustable_parameters)
            self.grid_size = (settings.gr_points_per_parameter **
                              no_adjust_params)

        # Initialize the RNG
        seed = self.baseseed + getattr(self, 'id', 0)
        random_params = random_parameter_grid(self.iterations,
                                              self.grid_size,
                                              seed=seed,
                                              *self.parameters)

        # Get the initial minimum
        params = next(random_params)
        minimum = self.function(*params)
        self.minimum_value = minimum

        # Generate random numbers and test their minimums
        for params in random_params:

            # Get the new minimum and see if it's better
            new_minimum = self.function(*params)

            if new_minimum < self.minimum_value:
                # If it is better, replace the new values in the parameters
                self.minimum_value = new_minimum

                for parameter, new_value in zip(self.parameters, params):
                    if not isinstance(parameter, MinimizerParameter):
                        continue
                    parameter.value = new_value

    # def minimize(self):
    #     """Minimize and return the results.
    #
    #     This is a wrapper to the parent minimize function that moves the seed
    #     forward by a defined amount so that subsequent runs of this minimization
    #     function returns different random numbers.
    #     """
    #     return_value = super(MCMinimizer, self).minimize()
    #     self.baseseed += 1000
    #     return return_value


