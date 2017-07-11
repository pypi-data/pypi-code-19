from featuretools import variable_types
from .aggregation_feature_base import AggregationFeature
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from scipy.stats import skew


class Sum(AggregationFeature):
    """
    Finds the sum of a numeric feature, or the number of 'True' values in a
    boolean feature.
    """
    function_name = "sum"
    apply_to = [(variable_types.Numeric,),
                (variable_types.Boolean,)]
    _variable_type = variable_types.Numeric
    max_stack_depth = 1
    stack_on = []
    stack_on_exclude = []

    def get_function(self):
        return lambda x: np.nan_to_num(x.values).sum(dtype=np.float)

    def _get_func_name(self):
        if self.base_features[0].variable_type == variable_types.Boolean:
            return "NUM_TRUE"
        else:
            return self.function_name.upper()


class PercentTrue(AggregationFeature):
    """
    Finds the percent of 'True' values in a boolean feature.
    """
    function_name = "percent_true"
    apply_to = [(variable_types.Boolean,)]
    _variable_type = variable_types.Numeric
    max_stack_depth = 1
    stack_on = []
    stack_on_exclude = []

    def get_function(self):
        def percent_true(x):
            if len(x) == 0:
                return np.nan
            return np.nan_to_num(x.values).sum(dtype=np.float) / len(x)
        return percent_true


class Mean(AggregationFeature):
    """Finds the mean value of a numeric feature ignoring nans"""
    function_name = "mean"
    apply_to = [(variable_types.Numeric,)]
    _variable_type = variable_types.Numeric
    max_stack_depth = 2
    # Mean can stack on anything
    stack_on = None
    stack_on_exclude = ["time_since"]
    stacks_on_self = True

    def get_function(self):
        return np.nanmean


class Median(AggregationFeature):
    """Finds the median value of any feature with well-ordered values."""
    function_name = "median"
    apply_to = [(variable_types.Numeric,),
                (variable_types.Ordinal,)]
    _variable_type = None
    max_stack_depth = 2
    # Median can stack on anything
    stack_on = None
    stacks_on_self = True

    def get_function(self):
        return np.median


class Std(AggregationFeature):
    """Finds the standard deviation of a numeric feature."""
    function_name = "std"
    apply_to = [(variable_types.Numeric,)]
    _variable_type = variable_types.Numeric
    max_stack_depth = 2
    # Std can stack on anything
    stack_on = None
    stacks_on_self = False

    def get_function(self):
        return np.std


class Mode(AggregationFeature):
    """Finds the most common element in a categorical feature."""
    function_name = "mode"
    apply_to = [(variable_types.Discrete,)]
    max_stack_depth = 1
    stack_on = None
    stack_on_exclude = []

    def get_function(self):
        def pd_mode(x):
            if x.mode().shape[0] == 0:
                return np.nan
            return x.mode().iloc[0]
        return pd_mode


class TopNMostCommon(AggregationFeature):
    """Finds the N most common elements in a categorical feature."""
    function_name = "topn_most_common"
    apply_to = [(variable_types.Discrete,)]
    max_stack_depth = 1
    stack_on = []
    stack_on_exclude = []
    expanding = True

    def __init__(self, base_feature, parent_entity, n=3):
        self.n = n
        super(TopNMostCommon, self).__init__(base_feature, parent_entity)

    @property
    def default_value(self):
        return np.zeros(self.n) * np.nan

    def get_expanded_names(self):
        names = []
        for i in range(1, self.n + 1):
            names.append(str(i) + self.get_name()[4:])
        return names

    def get_function(self):
        def pd_topn(f, x):
            return np.array(x.value_counts()[:f.n].index)
        return pd_topn


class Trend(AggregationFeature):
    """
    Fits a line to a variable over the time index of the child entity
    and returns the slope.
    """
    function_name = "trend"
    require_time_index = True
    apply_to = [(variable_types.Numeric, variable_types.Numeric),
                (variable_types.Numeric, variable_types.Datetime)]
    _variable_type = variable_types.Numeric
    max_stack_depth = None
    stack_on = []
    stack_on_exclude = []

    def can_apply(self, entity, prediction_entity_id, filters=None):
        if not super(Trend, self).can_apply(entity, prediction_entity_id, filters):
            return False
        # don't allow trend of time index (always 1)
        elif self.time_index_feature.hash() == self.base_features[0].hash():
            return False
        return True

    def get_function(self):
        def pd_trend(y, x):
            df = pd.DataFrame({"x": x, "y": y}).dropna()
            if df.shape[0] <= 2:
                return np.nan
            if isinstance(df['x'].iloc[0], (datetime, pd.Timestamp)):
                x = convert_datetime_to_floats(df['x'])
            else:
                x = df['x'].values

            if isinstance(df['y'].iloc[0], (datetime, pd.Timestamp)):
                y = convert_datetime_to_floats(df['y'])
            elif isinstance(df['y'].iloc[0], (timedelta, pd.Timedelta)):
                y = convert_timedelta_to_floats(df['y'])
            else:
                y = df['y'].values

            x = x - x.mean()
            y = y - y.mean()

            # prevent divide by zero error
            if len(np.unique(x)) == 1:
                return 0

            coefficients = np.polyfit(x, y, 1)

            return coefficients[0]
        return pd_trend


class Count(AggregationFeature):
    """Counts the number of non null values."""
    function_name = "count"
    _variable_type = variable_types.Numeric
    apply_to = [(variable_types.Categorical,),
                (variable_types.Numeric,)]
    stack_on = []
    stack_on_exclude = []
    max_stack_depth = 1
    only_id_variable = True
    default_value = 0

    def get_function(self):
        return lambda x: x.count()


class AvgTimeBetween(AggregationFeature):
    """
    Computes the average time between consecutive events
    using the time index of the entity

    Note: equivalent to Mean(Diff(time_index)), but more performant
    """
    # Potentially unnecessary if we add an trans_feat that
    # calculates the difference between events. DFS
    # should then calculate the average of that trans_feat
    # which amounts to AvgTimeBetween
    function_name = "avg_time_between"
    _variable_type = variable_types.Numeric
    apply_to = [(variable_types.Categorical, variable_types.Datetime),
                (variable_types.Numeric, variable_types.Datetime)]
    require_time_index = True
    max_stack_depth = 1
    stack_on = []
    stack_on_exclude = []
    only_id_variable = True

    def get_function(self):
        def pd_avg_time_between(y, x):
            """
            Assumes time scales are closer to order
            of seconds than to nanoseconds
            if times are much closer to nanoseconds
            we could get some floating point errors

            this can be fixed with another function
            that calculates the mean before converting
            to seconds
            """
            x = x.dropna()
            if x.shape[0] < 2:
                return np.nan
            if isinstance(x.iloc[0], (pd.Timestamp, datetime)):
                x = x.astype('int64')
                # use len(x)-1 because we care about difference
                # between values, len(x)-1 = len(diff(x))
                avg = ((x.max() - x.min())) / float(len(x) - 1)
            else:
                avg = (x.max() - x.min()) / float(len(x) - 1)

            avg = avg * 1e-9

            # long form:
            # diff_in_ns = x.diff().iloc[1:].astype('int64')
            # diff_in_seconds = diff_in_ns * 1e-9
            # avg = diff_in_seconds.mean()
            return avg
        return pd_avg_time_between


class Min(AggregationFeature):
    """Finds the minimum non-null value of a numeric feature."""
    function_name = "min"
    apply_to = [(variable_types.Numeric,)]
    _variable_type = None
    max_stack_depth = 1
    stack_on = []
    stack_on_exclude = []

    def get_function(self):
        return np.min


class Max(AggregationFeature):
    """Finds the maximum non-null value of a numeric feature."""
    function_name = "max"
    apply_to = [(variable_types.Numeric,)]
    _variable_type = None
    max_stack_depth = 1
    stack_on = []
    stack_on_exclude = []

    def get_function(self):
        return np.max


class NUnique(AggregationFeature):
    """
    Returns the number of unique categorical variables
    """
    function_name = "n_unique"
    # todo can we use discrete in apply_to instead?
    apply_to = [(variable_types.Categorical,),
                (variable_types.Ordinal,)]
    _variable_type = variable_types.Numeric
    max_stack_depth = 1
    stack_on = None
    stacks_on_self = False

    def get_function(self):
        return lambda x: x.nunique()


# TODO: Not implemented yet
class AvgAbsDiff(AggregationFeature):
    """
    Computes the mean of the absolute value of the difference
    between consecutive values

    Note: currently not implemented
    """
    function_name = "avg_abs_diff"
    apply_to = [(variable_types.Numeric,)]
    _variable_type = variable_types.Numeric
    max_stack_depth = 1
    stack_on = []
    stack_on_exclude = []

    def get_function(self):
        raise NotImplementedError("This feature has not been implemented")


# TODO: Not implemented yet
class Skew(AggregationFeature):
    function_name = "skew"
    apply_to = [(variable_types.Numeric,)]
    _variable_type = variable_types.Numeric
    stack_on = []
    stack_on_exclude = []
    max_stack_depth = 1

    def get_function(self):
        return skew


class Any(AggregationFeature):
    function_name = "any"
    apply_to = [(variable_types.Boolean,)]
    _variable_type = variable_types.Boolean
    stack_on = []
    stack_on_exclude = []
    max_stack_depth = 1

    def get_function(self):
        return np.any


class All(AggregationFeature):
    function_name = "all"
    apply_to = [(variable_types.Boolean,)]
    _variable_type = variable_types.Boolean
    stack_on = []
    stack_on_exclude = []
    max_stack_depth = 1

    def get_function(self):
        return np.all


# TODO: Not implemented yet
class Last(AggregationFeature):
    """
    Returns the last value

    Note: currently not implemented
    """
    function_name = "last"
    apply_to = [(variable_types.Categorical,),
                (variable_types.Ordinal,),
                (variable_types.Numeric,),
                (variable_types.Boolean,)]
    _variable_type = None
    stack_on = []
    stack_on_exclude = []
    max_stack_depth = 1

    def get_function(self):
        def pd_last(x):
            return x.iloc[-1]
        return pd_last


# TODO: Not implemented yet
class ConseqPos(AggregationFeature):
    function_name = "conseq_pos"
    apply_to = [(variable_types.Numeric,),
                (variable_types.Ordinal,)]
    _variable_type = variable_types.Numeric
    max_stack_depth = 1
    stack_on = []
    stack_on_exclude = []

    def get_function(self):
        raise NotImplementedError("This feature has not been implemented")


# TODO: Not implemented yet
class ConseqSame(AggregationFeature):
    function_name = "conseq_same"
    apply_to = [(variable_types.Categorical,),
                (variable_types.Ordinal,),
                (variable_types.Numeric,)]
    _variable_type = variable_types.Numeric
    max_stack_depth = 1
    stack_on = []
    stack_on_exclude = []

    def get_function(self):
        raise NotImplementedError("This feature has not been implemented")


# TODO: Not implemented yet
class TimeSinceLast(AggregationFeature):
    """
    Returns the difference between the time at which predictions
    are made and the time of the last recorded value in the entity

    Note: currently not implemented
    """
    function_name = "time_since_last"
    _variable_type = variable_types.Numeric
    apply_to = [(variable_types.Categorical,)]
    require_time_index = True
    max_stack_depth = 1
    stack_on = []
    stack_on_exclude = []
    only_id_variable = True

    def get_function(self):
        raise NotImplementedError("This feature has not been implemented")


# TODO: Not implemented yet
class MaxDiff(AggregationFeature):
    """
    Returns the maximum of the difference between consecutive values

    Note: currently not implemented
    """
    function_name = "max_diff"
    apply_to = [(variable_types.Numeric,),
                (variable_types.Datetime,)]
    _variable_type = None
    max_stack_depth = 1
    stack_on = []
    stack_on_exclude = []

    def get_function(self):
        raise NotImplementedError("This feature has not been implemented")


# TODO: Not implemented yet
class MinDiff(AggregationFeature):
    """
    Returns the minimum of the difference between consecutive values

    Note: currently not implemented
    """
    function_name = "min_diff"
    apply_to = [(variable_types.Numeric,),
                (variable_types.Datetime,)]
    _variable_type = None
    max_stack_depth = 1
    stack_on = []
    stack_on_exclude = []

    def get_function(self):
        raise NotImplementedError("This feature has not been implemented")


# TODO: Not implemented yet
class MeanDiff(AggregationFeature):
    """
    Returns the mean of the difference between consecutive values

    Note: currently not implemented
    """
    function_name = "mean_diff"
    apply_to = [(variable_types.Numeric,),
                (variable_types.Datetime,)]
    _variable_type = None
    max_stack_depth = 1
    stack_on = []
    stack_on_exclude = []

    def get_function(self):
        raise NotImplementedError("This feature has not been implemented")


ALL_AGG_FEATS = [Sum, Mean, Median, Std, Mode, Trend, Skew, Any, All,
                 Count, AvgTimeBetween, Min, Max, PercentTrue]


def convert_datetime_to_floats(x):
    first = int(x.iloc[0].value * 1e-9)
    x = pd.to_numeric(x).astype(np.float64).values
    dividend = find_dividend_by_unit(first)
    x *= (1e-9 / dividend)
    return x


def convert_timedelta_to_floats(x):
    first = int(x.iloc[0].total_seconds())
    dividend = find_dividend_by_unit(first)
    x = pd.TimedeltaIndex(x).total_seconds().astype(np.float64) / dividend
    return x


def find_dividend_by_unit(time):
    """
    Finds whether time best corresponds to a value in
    days, hours, minutes, or seconds
    """
    for dividend in [86400., 3600., 60.]:
        div = time / dividend
        if round(div) == div:
            return dividend
    return 1
