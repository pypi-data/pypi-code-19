import multiprocessing as mp
import os
import sys
from copy import copy
from collections import namedtuple

from . import settings

#: A minimization result with the minimum value and free MinimizerParameters.
Result = namedtuple('Result', 'minimum parameters')


class MinimizerParameter(object):
    """A parameter for the minimizer.

    Attributes
    ----------
    name: str or None, optional
        The name of the parameter
    value: float
        The value of the parameter. This starts as the initial value, and it
        will be replaced by the actual value as the parameter is minimized.
    range: (float, float)
        The range of values to sample for the parameter's value.
    """

    name = None
    value = None
    range = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)

    def __repr__(self):
        name = str(self.name) if self.name is not None else None
        value = str(self.value) if self.value is not None else None
        if name is not None and value is not None:
            return "=".join((name, value))
        else:
            return name or value


def worker(queue, results):
    """A worker function to process sub-minimizers.
    """

    while True:
        # Get the minimizer from the queue
        min = queue.get()

        # If there are no more sub-minimizers, then the job is done.
        if min is None:
            queue.task_done()
            break

        # Otherwise, run the minimization on the sub-minimizer
        min.no_runs = None
        min.minimize()
        queue.task_done()

        # And place the results in the results queue.
        results.put(min)
    return


class Minimizer(object):
    """Base class for the minimizer of functions.

    The base Minimizer class simply evaluates the function. Subclasses do more
    sophisticated things to minimize the function by implementing the
    :meth:`minimize_function`.

    Attributes
    ----------
    name: str, optional
        The name of the minimizer, used in the __repr__.
    description: str, optional
        The description of the minimizer, used in the __repr__.
    id: int
        The minimizer's id. If the minimizer is run over multiple runs (by
        setting :attr:`no_runs`), then each sub-minimizer will have a different
        id. These can be used to seed random number generators.
    no_runs: None or int, optional
        If None, this minimizer will only be run once.
        If it's a positive int, this minimizer will spawn ```no_runs```
        sub-minimizers and collect minimization statistics on each.
    keep_best: None or int, optional
        If None, all of the best minima will be returned as results.
        If it's a positive int, only the best ```keep_best``` number of results
        will be returned.
    minimum_value: None or float
        If None, the minimum has not yet been evaluated.
        If it's a float, this is the evaluated value of the minimum.
    parameters: list
        A list of the parameters to pass to the minimization function. These
        can included data and other objects. Items that are of type
        :obj:`MinimizerParameter` will be minimized.
        Note that parameters are conveniently added by the
        :meth:`add_parameters` method.
    function: function or object
        The function to minimize. This function should return a single
        floating point value like a chi^2 or an RMSD.


        .. note:: Since the Minimizer can spawn sub-minimizers to different
                  processes, the function must be pickleable. This means that
                  it cannot be a lambda function and that it must be either a
                  module-level function or object. If it's an object, the
                  ```__call__``` method should be implemented.
    """

    name = None
    description = None
    id = 0
    no_runs = None
    keep_best = None

    _minimum_value = None
    parameters = None
    function = None

    def __init__(self, print_status=None):
        self.preprocessors = []
        if print_status is None:
            self.print_status = settings.print_status
        else:
            self.print_status = print_status

    def add_parameters(self, *parameters):
        """Add parameters to the minimizer.

        Parameters
        ----------
        parameters:
            The data, arrays and parameters to pass to the :meth:`function` to
            minimize. Note that parameters that are :obj:`MinimizerParameter`
            objects will be minimized. Only these will be returned with the
            minimization result. Paramaters are passed to the function in the
            order that they were added by ``add_parameters``.
        """
        if not hasattr(self, 'parameters') or self.parameters is None:
            self.parameters = []
        self.parameters += parameters

    @property
    def adjustable_parameters(self):
        """Return a list of the adjustable parameters."""
        return [p for p in self.parameters if isinstance(p, MinimizerParameter)]

    @property
    def fixed_parameters(self):
        """Return a list of the fixed (non-adjustable) parameters."""
        return [p for p in self.parameters if isinstance(p, MinimizerParameter)]

    @property
    def minimum_value(self):
        """Return the minimum_value."""
        return self._minimum_value

    @minimum_value.setter
    def minimum_value(self, new_value):
        """Set the minimum value."""
        if self.print_status:
            # Get the terminal width
            _, columns =  os.popen('stty size', 'r').read().split()
            columns = int(columns)
            msg = "New minimum: {:.4f}".format(new_value)
            msg_len = len(msg)
            if msg_len < columns - 1:
                msg += " " * (columns - msg_len - 1)
            # print("\r" + msg),
            sys.stderr.write("\r" + msg)
            # sys.stderr.flush()
        self._minimum_value = new_value

    def add_subminimizer(self, preprocessor):
        """Add a sub-minimizer to run with this minimizer.
        
        Parameters
        ----------
        preprocessor: a minimizer (:class:`mollib.minimization.Minimizer` 
                      instance)
            A minimizer to run *before* this minimizer.
        """
        # At least one of the preprocessor, postprocessor should be a minimizer
        assert isinstance(preprocessor, Minimizer)
        self.preprocessors.append(preprocessor)

    def convert_to_result(self):
        """Convert and return this minimizer to a result object.

        None is returned if this minimizer was not minimized.
        """
        if self.minimum_value is not None and self.parameters is not None:
            free_parameters = [p for p in self.parameters
                               if isinstance(p, MinimizerParameter)]
            return Result(self.minimum_value, free_parameters)
        return None

    def minimize_function(self):
        """Minimize the :meth:`function`.

        This is the function implemented by subclasses to change the way
        different Minimizer subclasses will conduct a minimization.
        """
        parameters = []
        parameters += [p.value if hasattr(p, 'value') else p
                       for p in self.parameters]

        self.minimum_value = self.function(*parameters)

    def minimize(self):
        """Minimize and return the results.

        The minimizer may operate in single threaded mode, if :attr:`no_runs`
        is None, or in multi-threaded mode, if :attr:`no_runs` is an integer
        number.

        Returns
        -------
        result_list: list of name tuples or None
            [Result('minimum parameters']

            - The returned results are sorted by the minimum value.
            - Only the :attr:`keep_best` number of entries are returned. If
              this is None, then all items are returned.
            - The parameters are a list of parameters from the minimization.
              Only the :obj:`MinimizerParameter` objects are returned, since
              these are the free variables that are optimized in the
              minimization.
            - None is returned if there is nothing to do.
        """
        assert self.function is not None, ("The Minimizer function attribute "
                                           "must be assigned.")

        if self.no_runs is None:
            # Run preprocessors
            for preprocessor in self.preprocessors:
                # Initialize the preprocessor
                preprocessor.function = self.function
                if preprocessor.parameters is None:
                    preprocessor.parameters = self.parameters
                preprocessor.minimize_function()

                # Copy the optimized parameters back to this minimizer
                self.minimum_value = preprocessor.minimum_value
                self.parameters = preprocessor.parameters

            # Conduct this minimizer's minimization
            self.minimize_function()
            result_list = [self.convert_to_result(), ]
            return result_list

        elif isinstance(self.no_runs, int) and self.no_runs > 0:
            queue = mp.JoinableQueue()
            results = mp.Queue()

            num_consumers = mp.cpu_count()
            workers = [mp.Process(target=worker, args=(queue, results))
                       for i in range(num_consumers)]

            for w in workers:
                w.start()

            # Append to queue
            for cpu_id in range(self.no_runs):
                cp = copy(self)
                cp.no_runs = None
                for preprocessor in cp.preprocessors:
                    preprocessor.id = cpu_id
                cp.id = cpu_id
                queue.put(cp)

            # End the queue for each consumer
            for i in range(num_consumers):
                queue.put(None)

            # Wait for the worker to finish
            queue.join()

            # Process the results
            result_list = []
            while True:
                try:
                    result = results.get(block=False)
                except:
                    break

                # Append result if it's better than the other items stored in
                # the results list
                if self.keep_best is None:
                    result_list.append(result.convert_to_result())
                elif (len(result_list) < self.keep_best or
                      result_list[-1].minimum > result.minimum_value):

                    # Append and sort the result
                    result_list.append(result.convert_to_result())
                    result_list = sorted(result_list, key=lambda i:i[0])
                    result_list = result_list[0:self.keep_best]
                else:
                    continue
            return result_list

        else:
            return None

    def save(self, filename):
        """Save the minimizer parameter set to a file."""
        raise NotImplementedError

    def load(self, filename):
        """Load the minimizer parameter set from a file."""
        raise NotImplementedError