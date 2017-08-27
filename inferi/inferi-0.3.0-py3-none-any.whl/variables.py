"""Contains the base Variable class."""

from collections import Counter
from fuzz import Value
from math import sqrt
from .exceptions import EmptyVariableError

class Variable:
    """A Variable represents an ordered sequence of measurements. It is `not`
    the same as a Python variable - it represents variables in the statistics
    sense of the word.

    A Variable is a container `and` an iterable of its values, and in many
    respects behaves like a ``list``.

    :param \*values: The values to go into the Variable. These will usually be\
    numerical, but can be any type. If you provide one value, which is iterable,\
    and which isn't a string, the values of that iterable will become the values\
    of the Variable.
    :param str name: The name of the Variable.
    :param error: An iterable of error values to go with the values (optional).
    :raises EmptyVariableError: if no values are given.
    :raises TypeError: if the name given isn't a string.
    :raises TypeError: if error is not iterable.
    :raises ValueError: if the number of error values does not match number\
    of values.
    :raises TypeError: if non-numeric error values are given.
    :raises ValueError: if negative error values are given."""

    def __init__(self, *values, name="", error=None):
        if len(values) == 0:
            raise EmptyVariableError("Cannot create Variable with no values")
        if len(values) == 1:
            try:
                if isinstance(values[0], str): raise TypeError
                values = list(values[0])
            except TypeError:
                values = list(values)
        else:
            values = list(values)
        self._values = []
        self._error = []
        for value in values:
            if isinstance(value, Value):
                self._values.append(value.value())
                if not error: self._error.append(value.error())
            else:
                self._values.append(value)
                self._error.append(0)
        try:
            error is not None and iter(error)
        except: raise TypeError("Error {} is not iterable".format(error))
        if error is not None and len(error) != len(self._values):
            raise ValueError("Number of error values does not match values")
        for err in error or []:
            if not isinstance(err, (int, float)) or isinstance(err, bool):
                raise TypeError("Error {} is not numeric".format(err))
            if err < 0:
                raise ValueError("Error {} is negative".format(err))
        self._error = self._error if not error else error
        if not isinstance(name, str):
            raise TypeError("name '{}' is not a str".format(name))
        self._name = name


    def __repr__(self):
        if self._name:
            return "<Variable '{}' {}>".format(self._name, tuple(self._values))
        return "<Variable {}>".format(tuple(self._values))


    def __len__(self):
        return len(self._values)


    def __contains__(self, member):
        return member in self._values


    def __iter__(self):
        return iter(self._values)


    def __getitem__(self, key):
        return self._values[key]


    def __setitem__(self, key, value):
        self._values[key] = value


    def __add__(self, other):
        values = [Value(v, e) for v, e in zip(self._values, self._error)]
        if isinstance(other, Variable):
            if len(self) != len(other):
                raise ValueError("Cannot add Variables of different length")
            other = [Value(v, e) for v, e in zip(other._values, other._error)]
        else:
            other = [Value(other) for _ in values]
        sum_ = [v + o for v, o in zip(values, other)]
        return Variable([v.value() for v in sum_], error=[v.error() for v in sum_])


    def __radd__(self, other):
        return self + other


    def __sub__(self, other):
        values = [Value(v, e) for v, e in zip(self._values, self._error)]
        if isinstance(other, Variable):
            if len(self) != len(other):
                raise ValueError("Cannot add Variables of different length")
            other = [Value(v, e) for v, e in zip(other._values, other._error)]
        else:
            other = [Value(other) for _ in values]
        sum_ = [v - o for v, o in zip(values, other)]
        return Variable([v.value() for v in sum_], error=[v.error() for v in sum_])


    def get(self, index, error=False):
        """Returns the value at a given index. You can choose to have a
        fuzz ``Value`` object returned with associated error if you so wish.

        :param int index: The index of the value you want.
        :param bool error: If ``True`` a ``Value`` will be returned with the\
        relevant uncertainty.
        :returns: the requested value."""

        if error:
            return Value(self._values[index], self._error[index])
        return self._values[index]


    def set(self, index, value, error=None):
        """Updates a value in the Variable and, optionally, its error as well.

        :param int index: The index to update.
        :param value: The new value. If this is a fuzz ``Value`` object, the\
        numeric value will be extracted and its uncertainty used as the error\
        value.
        :param Number error: The error to be associated with the new value\
        (default is 0).
        :raises TypeError: if the error given is not numeric.
        :raises ValueError: if the error given is negative."""

        if isinstance(value, Value):
            self._values[index] = value.value()
            self._error[index] = value.error()
        self._values[index] = value
        if error is not None:
            if not isinstance(error, (int, float)) or isinstance(error, bool):
                raise TypeError("Error {} is not numeric".format(error))
            if error < 0:
                raise ValueError("Error {} is negative".format(error))
            self._error[index] = error


    def values(self, error=False):
        """Returns the values in the Variable.

        :param bool error: if ``True``, the values will be returned as fuzz\
        ``Value`` objects with associated error.
        :rtype: ``tuple``"""

        if error:
            return tuple([Value(v, e) for v, e in zip(self._values, self._error)])
        return tuple(self._values)


    def error(self):
        """Returns the error in the Variable.

        :rtype: ``tuple``"""

        return tuple(self._error)


    def add(self, value, error=None):
        """Adds a value to the Variable. You can supply an error value too,
        either with the ``error`` argument or by giving a fuzz ``Value`` as the
        value. Otherwise the error will be 0.

        :param value: The value to add.
        :param Number error: The error value to add.
        :raises TypeError: if the error given is not numeric.
        :raises ValueError: if the error given is negative."""

        if error is not None:
            if not isinstance(error, (int, float)) or isinstance(error, bool):
                raise TypeError("Error {} is not numeric".format(error))
            if error < 0:
                raise ValueError("Error {} is negative".format(error))
        if isinstance(value, Value):
            error = value.error() if error is None else error
            value = value.value()
        self._values.append(value)
        self._error.append(error if error is not None else 0)



    def remove(self, value):
        """Removes a value from the Variable.

        :param value: The value to remove.
        :raises EmptyVariableError: if you try to remove the only value."""

        if len(self._values) == 1:
            raise EmptyVariableError("Cannot remove last value from Variable")
        if value in self._values:
            self._error.pop(self._values.index(value))
            self._values.remove(value)


    def pop(self, index=-1, error=False):
        """Removes and returns the value at a given index - by default the last
        object in the Variable.

        :param int index: The index to remove at (default is ``-1``).
        :param bool error: if ``True``, the value will be returned as a fuzz\
        ``Value`` with associated error.
        :raises EmptyVariableError: if you try to pop the only value.
        :returns: the specified value."""

        if len(self._values) == 1:
            raise EmptyVariableError("Cannot pop last value from Variable")
        if error:
            return Value(self._values.pop(index), self._error.pop(index))
        self._error.pop(index)
        return self._values.pop(index)


    def name(self, name=None):
        """Returns the name of the Variable. If a value is given,
        the name will be updated to this (provided it is a string).

        :param str name: If given, this will be made the new name.
        :raises TypeError: if the name given is not a string."""

        if name is None:
            return self._name
        else:
            if not isinstance(name, str):
                raise TypeError("name '{}' is not a str".format(name))
            self._name = name


    def length(self):
        """The length of the Variable - the number of values it has.

        :rtype: ``int``"""

        return len(self)


    def max(self, error=False):
        """Returns the largest value.

        :param bool error: if ``True``, the value will be returned as a fuzz\
        ``Value`` with associated error."""

        return max(self.values(error=error))


    def min(self, error=False):
        """Returns the smallest value.

        :param bool error: if ``True``, the value will be returned as a fuzz\
        ``Value`` with associated error."""

        return min(self.values(error=error))


    def sum(self, error=False):
        """Returns the sum of the values in the Variable. This will usually be
        a number but depends on the object types in the Variable.

        :param bool error: if ``True``, the value will be returned as a fuzz\
        ``Value`` with associated error."""

        return sum(self.values(error=error))


    def mean(self, error=False):
        """Returns the mean of the values - their sum divided by the number of
        values.

        :param bool error: if ``True``, the value will be returned as a fuzz\
        ``Value`` with associated error."""

        return self.sum(error=error) / self.length()


    def median(self):
        """Returns the median value - the value that occurs midway through
        when the values are sorted. If there is an even number, the midpoint
        between the two median values will be returned."""

        values = sorted(self.values())
        if len(values) % 2:
            return values[int((len(values) - 1) / 2)]
        midway = int(self.length() / 2)
        return (values[midway - 1] + values[midway]) / 2


    def frequencies(self):
        """Returns the frequencies of the values in the Variable.

        :rtype: ``Counter``"""

        return Counter(self.values())


    def mode(self):
        """Returns the mode value - the value that occurs the most often. If
        more than one value meets this criteria, ``None`` is returned."""

        values = self.frequencies()
        highest_frequency = max(values.values())
        if len([v for v in values if values[v] == highest_frequency]) == 1:
            return values.most_common()[0][0]


    def range(self, error=False):
        """Returns the range of the values - the difference between the
        largest and smallest values.

        :param bool error: if ``True``, the value will be returned as a fuzz\
        ``Value`` with associated error."""

        return self.max(error=error) - self.min(error=error)


    def variance(self, population=False):
        """Returns the variance of the values - the mean square deviation of
        the values from the mean. The values really have to be numerical for
        this to be meaningful.

        You can elect to get the population variance if you wish, which uses `N`
        rather than `N - 1` as the denominator.

        :param bool population: If ``True``, the population variance will be\
        returned (default is ``False``).
        :rtype: ``float``"""

        return sum([
         (value - self.mean()) ** 2 for value in self.values()
        ]) / (self.length() - (not population))


    def st_dev(self, population=False):
        """Returns the standard deviation of the values, the square root of
        the :py:meth:`.variance` and a measure of deviation from the mean.
        As with that metric, you need numerical data for this to be sensible.

        You can elect to get the population deviation if you wish, which uses
        `N` rather than `N - 1` as the denominator.

        :param bool population: If ``True``, the population deviation will be\
        returned (default is ``False``).
        :rtype: ``float``"""

        return sqrt(self.variance(population=population))


    def zscore(self, value, population=False):
        """The z-score of a value is how many standard deviations it is from
        the mean.

        :param value: The value who's z-score you want to know.
        :param bool population: If ``True``, the population deviation will be\
        used (default is ``False``)."""

        return (value - self.mean()) / self.st_dev(population=population)


    def covariance_with(self, variable):
        """Returns the covariance between this Variable and another Variable.
        This is a measure of how the variance of the two series reflect each
        other, and is a measure of correlation.

        :param Variable variable: The other Variable. It must be the same\
        length as this one.
        :raises TypeError: if something other than a Variable is given.
        :raises ValueError: if Variables of different length are given."""

        if not isinstance(variable, Variable):
            raise TypeError("{} is not a Variable".format(str(variable)))
        if self.length() != variable.length():
            raise ValueError(
             "length {} is not length {} - covariance not possible".format(
              self.length(), variable.length()
             )
            )
        this_mean = self.mean()
        other_mean = variable.mean()
        square_deviations = sum([(value - this_mean) * (other - other_mean)
         for value, other in zip(self.values(), variable.values())])
        mean_square_deviation = square_deviations / (self.length() - 1)
        return mean_square_deviation


    def correlation_with(self, variable):
        """Returns the correlation of one Variable with another. This differs
        from :py:meth:`covariance_with` in that it is normalised to be
        between -1 and 1, so the maginitude of the result is important, rather
        than just the sign as is the case with covariance.

        All the same requirements apply - the object given must be a Variable,
        and they must be the same length.

        :param Variable variable: The other Variable. It must be the same\
        length as this one."""

        covariance = self.covariance_with(variable)
        sd_product = self.st_dev() * variable.st_dev()
        return covariance / sd_product


    @staticmethod
    def average(*variables, sd_err=False):
        """This is a static method which averages one or more Variables. The
        Variables must be of equal length.

        :param \*variables: One or more Variables.
        :raises TypeError: if non-Variables are given.
        :raises TypeError: if zero Variables are given.
        :raises ValueError: if the Variables are not of equal length.
        :rtype: ``Variable``"""

        for variable in variables:
            if not isinstance(variable, Variable):
                raise TypeError("{} is not a Variable".format(variable))
        if len(variables) < 1:
            raise TypeError("Need at least one Variable to average.")
        if len(set([var.length() for var in variables])) != 1:
            raise ValueError("Cannot average Variables of different lengths")

        variables = [var.values(error=True) for var in variables]
        sum_ = [sum(values) for values in zip(*variables)]
        average = [val / len(variables) for val in sum_]
        values = [val.value() for val in average]
        error = [val.error() for val in average]
        if sd_err:
            error = [
             Variable(*vals).st_dev(population=True) for vals in zip(*variables)
            ]
        return Variable(values, error=error)
