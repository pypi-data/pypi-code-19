from .primitive_base import PrimitiveBase, IdentityFeature
from featuretools.variable_types import (Discrete, Numeric, Categorical, Boolean,
                                         Ordinal, Text, Datetime, Variable,
                                         TimeIndex, DatetimeTimeIndex, Id)

import datetime
import os
import pandas as pd
import numpy as np
from pandas.core.common import is_timedelta64_dtype
current_path = os.path.dirname(os.path.realpath(__file__))
FEATURE_DATASETS = os.path.join(os.path.join(current_path, '..'), 'feature_datasets')


class TransformPrimitive(PrimitiveBase):
    """Feature for entity that is a based off one or more other features
        in that entity"""
    rolling_function = False

    def __init__(self, *base_features):
        self.base_features = [self._check_feature(f) for f in base_features]
        if any(bf.expanding for bf in self.base_features):
            self.expanding = True
        assert len(set([f.entity for f in self.base_features])) == 1, \
            "More than one entity for base features"
        super(TransformPrimitive, self).__init__(self.base_features[0].entity,
                                                 self.base_features)

    def _get_name(self):
        name = u"{}(".format(self.name.upper())
        name += u", ".join(f.get_name() for f in self.base_features)
        name += u")"
        return name

    @property
    def default_value(self):
        return self.base_features[0].default_value


class IsNull(TransformPrimitive):
    """For each value of base feature, return true if value is null"""
    name = "is_null"
    input_types = [Variable]
    return_type = Boolean

    def get_function(self):
        return lambda array: pd.isnull(pd.Series(array))


class Absolute(TransformPrimitive):
    """Absolute value of base feature"""
    name = "absolute"
    input_types = [Numeric]
    return_type = Numeric

    def get_function(self):
        return lambda array: np.absolute(array)


class TimeSincePrevious(TransformPrimitive):
    """ Compute the time since the previous instance for each instance in a time indexed entity"""
    name = "time_since_previous"
    input_types = [DatetimeTimeIndex, Id]
    return_type = Numeric

    def __init__(self, time_index, group_feature):
        """Summary

        Args:
            base_feature (:class:`PrimitiveBase`): base feature
            group_feature (None, optional): variable or feature to group
                rows by before calculating diff

        """
        group_feature = self._check_feature(group_feature)
        assert issubclass(group_feature.variable_type, Discrete), \
            "group_feature must have a discrete variable_type"
        self.group_feature = group_feature
        super(TimeSincePrevious, self).__init__(time_index, group_feature)

    def _get_name(self):
        return u"time_since_previous_by_%s" % self.group_feature.get_name()

    def get_function(self):
        def pd_diff(base_array, group_array):
            bf_name = 'base_feature'
            groupby = 'groupby'
            grouped_df = pd.DataFrame.from_dict({bf_name: base_array, groupby: group_array}).groupby(groupby).diff()
            return grouped_df[bf_name].apply(lambda x:
                                             x.total_seconds())
        return pd_diff


class Day(TransformPrimitive):
    """Transform Datetime feature into the day (0 - 30) of the month,
       or Timedelta features into number of days they encompass"""
    name = "day"
    input_types = [Datetime]
    return_type = Ordinal

    def get_function(self):
        return pd_time_unit("day")


class Hour(TransformPrimitive):
    """Transform Datetime feature into the hour (0 - 23) of the day,
       or Timedelta features into number of hours they encompass"""
    name = "hour"
    input_types = [Datetime]
    return_type = Ordinal

    def get_function(self):
        return pd_time_unit("hour")


class Minute(TransformPrimitive):
    """Transform Datetime feature into the minute (0 - 59) of the hour,
       or Timedelta features into number of minutes they encompass"""
    name = "minute"
    input_types = [Datetime]
    return_type = Ordinal

    def get_function(self):
        return pd_time_unit("minute")


class Week(TransformPrimitive):
    """Transform Datetime feature into the week (0 - 52) of the year
       or Timedelta features into number of weeks they encompass"""
    name = "week"
    input_types = [Datetime]
    return_type = Ordinal

    def get_function(self):
        return pd_time_unit("week")


class Month(TransformPrimitive):
    """Transform Datetime feature into the month (0 - 11) of the year,
       or Timedelta features into number of months they encompass """
    name = "month"
    input_types = [Datetime]
    return_type = Ordinal

    def get_function(self):
        return pd_time_unit("month")


class Year(TransformPrimitive):
    """Transform Datetime feature into the year,
       or Timedelta features into number of years they encompass"""
    name = "year"
    input_types = [Datetime]
    return_type = Ordinal

    def get_function(self):
        return pd_time_unit("year")


class Weekend(TransformPrimitive):
    """Transform Datetime feature into the boolean of Weekend"""
    name = "is_weekend"
    input_types = [Datetime]
    return_type = Boolean

    def get_function(self):
        return lambda df: pd_time_unit("weekday")(df) > 4


class Weekday(TransformPrimitive):
    """Transform Datetime feature into the day (0 - 6) of the Week"""
    name = "weekday"
    input_types = [Datetime]
    return_type = Boolean

    def get_function(self):
        return pd_time_unit("weekday")

# class Like(TransformPrimitive):
#     """Equivalent to SQL LIKE(%text%)
#        Returns true if text is contained with the string base_feature
#     """
#     name = "like"
#     input_types =  [(Text,), (Categorical,)]
#     return_type = Boolean

#     def __init__(self, base_feature, like_statement, case_sensitive=False):
#         self.like_statement = like_statement
#         self.case_sensitive = case_sensitive
#         super(Like, self).__init__(base_feature)

#     def get_function(self):
#         def pd_like(df, f):
#             return df[df.columns[0]].str.contains(f.like_statement,
#                                                   case=f.case_sensitive)
#         return pd_like


class TimeSince(TransformPrimitive):
    """
    For each value of the base feature, compute the timedelta between it and a datetime
    """
    name = "time_since"
    input_types =  [DatetimeTimeIndex]
    return_type = Numeric
    uses_calc_time = True

    def get_function(self):
        def pd_time_since(array, time):
            if time is None:
                time = datetime.now()
            # TODO: check if this is the same, and replace
            # time_diff = time - df[df.columns[0]]
            # return pd_time_unit('day')(time_diff, f)
            return pd.Series(array).apply(lambda x, days_in_seconds=86400:
                                          (time - x).total_seconds() / days_in_seconds)
        return pd_time_since


class IsIn(TransformPrimitive):
    """
    For each value of the base feature, checks whether it is in a list that is provided.
    """
    name = "isin"
    input_types =  [Variable]
    return_type = Boolean

    def __init__(self, base_feature, list_of_outputs=None):
        self.list_of_outputs = list_of_outputs
        super(IsIn, self).__init__(base_feature)

    def get_function(self):
        def pd_is_in(array, list_of_outputs=self.list_of_outputs):
            if list_of_outputs is None:
                list_of_outputs = []
            return pd.Series(array).isin(list_of_outputs)
        return pd_is_in

    def _get_name(self):
        return u"%s.isin(%s)" % (self.base_features[0].get_name(),
                                str(self.list_of_outputs))


class Diff(TransformPrimitive):
    """
    For each value of the base feature, compute the difference between it and the previous value.

    If it is a Datetime feature, compute the difference in seconds
    """
    name = "diff"
    input_types =  [Numeric, Id]
    return_type = Numeric

    def __init__(self, base_feature, group_feature):
        """Summary

        Args:
            base_feature (:class:`PrimitiveBase`): base feature
            group_feature (:class:`PrimitiveBase`): variable or feature to group
                rows by before calculating diff

        """
        self.group_feature = self._check_feature(group_feature)
        super(Diff, self).__init__(base_feature, group_feature)

    def _get_name(self):
        base_features_str = self.base_features[0].get_name() + u" by " + self.group_feature.get_name()
        return u"%s(%s)" % (self.name.upper(), base_features_str)

    def get_function(self):
        def pd_diff(base_array, group_array):
            bf_name = 'base_feature'
            groupby = 'groupby'
            grouped_df = pd.DataFrame.from_dict({bf_name: base_array, groupby: group_array}).groupby(groupby).diff()
            return grouped_df[bf_name]
        return pd_diff


class Not(TransformPrimitive):
    name = "not"
    input_types =  [Boolean]
    return_type = Boolean

    def _get_name(self):
        return u"NOT({})".format(self.base_features[0].get_name())

    def _get_op(self):
        return "__not__"

    def get_function(self):
        return lambda array: np.logical_not(array)


def pd_time_unit(time_unit):
    def inner(array):
        if is_timedelta64_dtype(array[0]):
            seconds = pd.Series(pd.TimedeltaIndex(array).total_seconds())
            seconds = seconds.values
            if time_unit == 'second':
                return seconds
            elif time_unit == 'minute':
                return seconds / 60
            elif time_unit == 'hour':
                return seconds / 3600
            elif time_unit == 'day':
                return seconds / (3600 * 24)
            elif time_unit == 'week':
                return seconds / (3600 * 24 * 7)
            elif time_unit == 'month':
                return seconds / (3600 * 24 * 30.42)
            elif time_unit == 'year':
                return seconds / (3600 * 24 * 365.25)
            else:
                raise ValueError("Unit {} not allowed in time unit row functions".format(time_unit))
        else:
            return getattr(pd.DatetimeIndex(array), time_unit)
    return inner

# TODOs
# class Percentile(TransformPrimitive):