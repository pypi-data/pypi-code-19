"""Contains the basic Series class and its methods."""

from collections import Counter
from math import sqrt
from .exceptions import EmptySeriesError

class Series(list):
    """A Series represents a set of measurements made on a collection of
    entities, such as the heights of a group of football players, or the
    favourite colours of a class of school children.

    It is basically an extended list.

    :param \*values: The measurements, as positional arguments.
    :param str name: The name of this set of measurement.
    :raises EmptySeriesError: If you try to make a series with no values."""

    def __init__(self, *values, name=None, sample=True, **kwargs):
        if not values:
            raise EmptySeriesError("Cannot make a Series with no values")
        list.__init__(self, [*values], **kwargs)

        if not isinstance(name, str) and name is not None:
            raise TypeError("Series name must be str, not '%s'" % str(name))
        self._name = name
        if not isinstance(sample, bool):
            raise TypeError("Series sample must be bool, not '%s'" % str(sample))
        self._sample = sample


    def __repr__(self):
        if self._name:
            return "<'%s': %s>" % (self._name, list.__repr__(self))
        else:
            return "<Series: %s>" % list.__repr__(self)


    def length(self):
        """Returns the number of measurements in this series.

        :rtype: ``int``"""

        return len(self)


    def sample(self, sample=None):
        """Indicates whether the series represents a sample (in which case this
        method will be ``True``) or an entire population (``False``). This can
        affect the calculation of certain metrics, such as standard deviation.

        :param bool sample: if given, the sample will be updated to this."""

        if sample is None:
            return self._sample
        else:
            if not isinstance(sample, bool):
                raise TypeError(
                 "Series sample must be bool, not '%s'" % str(sample)
                )
            self._sample = sample


    def remove(self, *args, **kwargs):
        if self.length() == 1:
            raise EmptySeriesError("Cannot remove a series' last item")
        list.remove(self, *args, **kwargs)


    def pop(self, *args, **kwargs):
        if self.length() == 1:
            raise EmptySeriesError("Cannot pop a series' last item")
        list.pop(self, *args, **kwargs)


    def name(self, name=None):
        """Returns the series' name. If an argument is given, the name will
        be set to that value.

        :param str name: The new name of this measurement to set.
        :rtype: ``str``"""

        if name is None:
            return self._name
        else:
            if not isinstance(name, str):
                raise TypeError(
                 "Series name must be str, not '%s'" % str(name)
                )
            self._name = name


    def mean(self):
        """Returns the arithmetic mean of the series.

        :rtype: ``float``"""

        return sum(self) / len(self)


    def median(self):
        """Returns the median of the series.

        :rtype: ``float``"""

        sorted_values = sorted(self)
        if self.length() % 2:
            return sorted_values[int((self.length() / 2) - 0.5)]
        else:
            midway = int(self.length() / 2)
            return (sorted_values[midway - 1] + sorted_values[midway]) / 2


    def mode(self):
        """Returns the mode of the series. If there more than one value occurs
        the most frequently, ``None`` will be returned.

        :rtype: ``float``"""

        values = Counter(self)
        highest_frequency = max(values.values())
        modes = [value for value in values if values[value] == highest_frequency]
        if len(modes) == 1:
            return modes[0]


    def range(self):
        """Returns the range of the series - the distance between the largest
        and smallest values.

        :rtype: ``float``"""

        return max(self) - min(self)


    def variance(self):
        """Returns the variance of the series - the mean squared deviation from
        the mean for the values in the series.

        Note that the value returned will depend on whether the series is a
        sample (the default) or a population.

        :rtype: ``float``"""

        mean = self.mean()
        square_deviation = [(x - mean) ** 2 for x in self]
        square_deviation = sum(square_deviation)
        denominator = self.length() - 1 if self.sample() else self.length()
        return square_deviation / denominator


    def standard_deviation(self):
        """Returns the standard deviation of the series - the mean deviation
        from the mean for the values in the series.

        Note that the value returned will depend on whether the series is a
        sample (the default) or a population.

        :rtype: ``float``"""

        return sqrt(self.variance())


    def covariance_with(self, other_series):
        """Returns the covariance between this series and another series. This
        is a measure of how the variance of the two series reflect each other,
        and is a measure of correlation.

        :param Series other_series: The other series. It must be the same\
        length as this one."""

        if not isinstance(other_series, Series):
            raise TypeError(
             "Covariance must be between two Series, not Series and '%s'" % str(
              other_series
             )
            )
        if self.length() != other_series.length():
            raise ValueError("'%s' and '%s' are not the same length" % (
             str(self), str(other_series))
            )
        this_mean = self.mean()
        other_mean = other_series.mean()
        square_deviations = sum([(value - this_mean) * (
         other_series[index] - other_mean
        ) for index, value in enumerate(self)])
        mean_square_deviation = square_deviations / (self.length() - 1)
        return mean_square_deviation


    def correlation_with(self, other_series):
        """Returns the correlation of one series with another. This differs
        from :py:meth:`covariance_with` in that it is normalised to be
        between -1 and 1, so the maginitude of the result is important, rather
        than just the sign as is the case with covariance.

        :param Series other_series: The other series. It must be the same\
        length as this one."""

        covariance = self.covariance_with(other_series)
        sd_product= self.standard_deviation() * other_series.standard_deviation()
        return covariance / sd_product
