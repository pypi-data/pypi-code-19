"""
Functions for the random access of parameter values in multidimensional 
parameter space.
"""
from math import floor

from mollib.utils.rng import unique_random_numbers
from .minimizer import MinimizerParameter


def random_parameter_grid(iterations, grid_size, *parameters, **kwargs):
    """Produce a generator for parameters sampled randomly on a 
    multidimensional grid. (One dimension for each parameter 
    (:obj:`mollib.minimization.MinimizerParameter`))
    
    Parameters
    ----------
    iterations: int
        The number of iterations (samples) to produce.
    grid_size: int
        The total number of grid points in the multidimensional parameter 
        space.
    chunks: int, optional
        Split the random numbers into the following chunks. See the
        unique_random_numbers function 
        (:func:`mollib.utils.rng.unique_random_numbers`)
    seed: int, optional
        Use the given seed for the random number generator.
        (:func:`mollib.utils.rng.unique_random_numbers`)
        
    Returns
    -------
    *randomized_parameters: tuple of parameters
        The parameters returned in which the minimizer parameters 
        (:obj:`mollib.minimization.MinimizerParameter`) have been randomized.
    
    Examples
    --------
    >>> from mollib.minimization import MinimizerParameter
    >>> p = MinimizerParameter(value=2.5, range=(-4.0, 5.0))
    >>> parameters = ('test', p, 2.5)
    >>> g = random_parameter_grid(3, 10, seed=0, *parameters)
    >>> for i in g:
    ...     print(i)
    ['test', -3.0, 2.5]
    ['test', -1.0, 2.5]
    ['test', 4.0, 2.5]
    """
    # Initialize parameters
    seed = kwargs.get('seed', None)
    chunks = kwargs.get('chunks', 5)

    # Determine the number of parameters and the number of adjustable parameters
    no_adj_params = len([p for p in parameters
                         if isinstance(p, MinimizerParameter)])

    # Determine the number of points to sample along each adjustable parameter
    # ex: grid_size = 10,000,000, no_adj_params = 5,
    #     points_per_param = 25
    if no_adj_params > 0:
        points_per_param = int(floor(float(grid_size)
                                     ** float(1./no_adj_params)))
    else:
        points_per_param = 1

    # Generate the random steps and break these into a series of indices
    # for each adjustable parameter
    generator = unique_random_numbers(num_steps=iterations,
                                      total_size=grid_size,
                                      chunks=chunks,
                                      seed=seed)
    for random_num in generator:
        # Convert the random number into a set of indices, one for each
        # adjustableparameter
        indices = _loop_indices(random_num, points_per_param, no_adj_params)

        # The returned values
        parameter_values = []

        for parameter in parameters:
            # See if it's a non-adjustable parameter
            if not isinstance(parameter, MinimizerParameter):
                parameter_values.append(parameter)

            # In this case, it's an adjustable parameter
            else:
                parameter_index = indices.pop()
                min_value = parameter.range[0]
                max_value = ((parameter.range[1] - parameter.range[0]) *
                             float(points_per_param) /
                             float(points_per_param - 1.))

                value = (min_value +
                         (float(parameter_index) * max_value /
                          float(points_per_param)))
                parameter_values.append(value)

        yield parameter_values

    return


def _loop_indices(index, points_per_param, no_adj_params):
    """Convert an index number into a tuple with a series of loop indices for a
    multidimensional data set with multilayered loops.
    
    Parameters
    ----------
    index: int
        The index number to convert into a series of loop indicies.
    points_per_param: int
        The number of points to sample in each dimension
    no_adj_params: int
        The number of dimensions.

    Returns
    -------
    loop_indices: tuple of int
        The index numbers.

    >>> _loop_indices(883, 10, 3)
    [8, 8, 3]
    >>> _loop_indices(83, 10, 2)
    [8, 3]
    >>> _loop_indices(440, 10, 3)
    [4, 4, 0]
    >>> _loop_indices(440, 10, 4)
    [0, 4, 4, 0]
    >>> _loop_indices(1440, 10, 4)
    [1, 4, 4, 0]
    >>> _loop_indices(9999, 10, 4)
    [9, 9, 9, 9]
    >>> _loop_indices(3, 10, 4)
    [0, 0, 0, 3]
    """
    indices = []

    for dim in range(no_adj_params - 1, 0, -1):
        i = floor(index / points_per_param ** dim)
        i = int(i)

        indices.append(i)
        index -= i * points_per_param ** dim

    indices.append(index)
    return indices


