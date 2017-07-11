from .aggregation_feature_base import AggregationFeature
from featuretools import variable_types
from featuretools.utils.wrangle import _check_timedelta
import numpy as np
import math
import pandas as pd
from ..cython_utils.pandas_backend import utils as c_utils


class SlidingWindow(AggregationFeature):
    """
    Slides a window of window_size along a child entity (going back a fixed
    amount defined by use_previous), aggregating the data
    in each window to return an array of size ceil(use_previous / window_size)

    Optional gap parameter offsets windows from each other, so that the array
    returned is of size ceil(use_previous / (window_size + gap))
    """
    require_time_index = True
    expanding = True
    apply_to = [(variable_types.Variable, variable_types.Numeric),
                (variable_types.Variable, variable_types.Datetime)]
    only_id_variable = False
    _variable_type = None

    def __init__(self, function_name, base_feature, parent_entity,
                 use_previous=None, window_size=None,
                 gap=None, where=None):
        self.function_name = "sliding_" + function_name
        self._agg_func_name = function_name
        self.window_size = _check_timedelta(window_size)
        self.gap = gap
        assert use_previous is not None, "use_previous must be defined for SlidingWindow feature"
        assert self.window_size is not None, "window_size must be defined for SlidingWindow feature"
        use_previous = _check_timedelta(use_previous)
        assert use_previous.is_absolute() == self.window_size.is_absolute(), (
            "units of use_previous and window_size must either both be observations-based",
            "or both be time-based")
        super(SlidingWindow, self).__init__(base_feature,
                                            parent_entity,
                                            use_previous=use_previous,
                                            where=where)

    @property
    def default_value(self):
        return np.empty(self.get_buckets()) * np.nan

    def _window_str(self):
        window_str = ", window_size = {}".format(self.window_size.get_name())
        if self.gap:
            window_str += ", gap = {}".format(self.gap.get_name())
        return window_str

    def _get_name(self):
        where_str = self._where_str()
        use_prev_str = self._use_prev_str()
        window_str = self._window_str()
        base_features_str = self._base_feature_str()

        return "%s(%s.%s%s%s%s)" % (self._get_func_name(),
                                    self.child_entity.name,
                                    base_features_str,
                                    where_str, use_prev_str, window_str)

    def get_expanded_names(self):
        return [self.get_name() + "(" + str(b) + ")"
                for b in range(self.get_buckets())]

    def get_buckets(self):
        if self.window_size.is_absolute() and self.window_size.unit != 'u':
            upv = self.use_previous.value_in_seconds
            wv = self.window_size.value_in_seconds
            if not self.gap:
                gap = 0
            else:
                gap = self.gap.value_in_seconds
            return int(math.ceil(float(upv) / (wv + gap)))

        else:
            if not self.gap:
                gap = 0
            else:
                gap = self.gap.value
            return int(math.ceil(float(self.use_previous.value) / (self.window_size.value + gap)))

    def get_function(self):
        rolling_func = self._agg_func_name

        def pd_sliding(f, var, time_index):
            values = var.loc[:]
            win = f.window_size.value
            if f.gap:
                gap = f.gap.value
            else:
                gap = 0

            assert gap >= 0 or not f.window_size.is_absolute(), "negative gap values not yet supported on absolute time indexes"
            assert gap == 0 or not f.window_size.unit == 'u', "gap values not yet supported on generic time units"
            assert win + gap > 0, "Negative gap (functioning as overlap) must be less than window_size"
            win += gap

            unit = f.window_size.unit
            assert f.use_previous.is_absolute() == f.window_size.is_absolute()
            assert f.gap is None or f.use_previous.is_absolute() == f.gap.is_absolute()
            # assert unit != 'u', "Generic units not yet supported"
            if f.window_size.is_absolute() and unit != 'u':
                win = str(win) + freq_time_unit(unit)

            buckets = f.get_buckets()
            if f.window_size.is_absolute():
                if unit == 'u':
                    # TODO: gap case
                    windows = np.arange(time_index.iloc[-1],
                                        time_index.iloc[0] - win, -win)
                    # if first element of time_index is at exact window boundary
                    # windows will contain an extra element
                    windows = windows[:buckets + 1][::-1]
                    binned = pd.cut(time_index, windows).to_frame('bins')
                    binned.index.name = 'time_index'
                    binned.reset_index(inplace=True)
                    values = values.to_frame('values')
                    values[['time_index', 'bins']] = binned[['time_index', 'bins']]
                    sampled = getattr(values.groupby('bins')['values'], rolling_func)().values
                else:
                    # TODO: redo absolute time case to be more like generic unit case
                    values.index = time_index
                    if values.index.shape[0] < 2:
                        base = 0
                    else:
                        full_window = pd.Timedelta(win, unit)
                        # pandas has a really weird base argument
                        # need base to make sure frequency windows end at the actual
                        # last value of values
                        base = get_time_base(values.index.values[-1], full_window, unit)
                    sampled = values.resample(win,
                                              base=base,
                                              closed='right')
                    if gap > 0:
                        # very much a slow hack
                        # pandas doesn't let you see the frequency buckets when you aggregate
                        # so have to remove the values within the gaps beforehand
                        freqs = sampled.asfreq()
                        gap_diff = f.window_size
                        freqs_gap_end = freqs.index - gap_diff
                        freqs_gap_start = freqs_gap_end - f.gap
                        for i, freq in enumerate(freqs_gap_start):
                            values = values[(values.index <= freq) | (values.index > freqs_gap_end[i])]
                        sampled = values.resample(win, base=base, closed='right')
                    sampled = getattr(sampled, rolling_func)().values
            else:
                sampled = sampled_and_agg_observations(values, f.window_size.value, gap, rolling_func)

            extended = np.zeros(buckets)
            extended.fill(np.nan)
            extended[:sampled.shape[0]] = sampled[::-1]
            extended = extended[::-1]
            return extended
        return pd_sliding


class SlidingMean(SlidingWindow):
    """
    Take mean of data in each window defined by params
    """
    apply_to = [(variable_types.Numeric, variable_types.Numeric),
                (variable_types.Numeric, variable_types.Datetime)]
    _variable_type = variable_types.Numeric

    def __init__(self, base_feature, parent_entity, use_previous=None,
                 window_size=None, gap=None, where=None):
        function_name = "mean"
        super(SlidingMean, self).__init__(function_name,
                                          base_feature,
                                          parent_entity,
                                          use_previous=use_previous,
                                          window_size=window_size,
                                          gap=gap,
                                          where=None)


class SlidingSum(SlidingWindow):
    """
    Take sum of data in each window defined by params
    """
    apply_to = [(variable_types.Numeric, variable_types.Numeric),
                (variable_types.Numeric, variable_types.Datetime)]
    _variable_type = variable_types.Numeric

    def __init__(self, base_feature, parent_entity, use_previous=None,
                 window_size=None, gap=None, where=None):
        function_name = "sum"
        super(SlidingSum, self).__init__(function_name,
                                         base_feature,
                                         parent_entity,
                                         use_previous=use_previous,
                                         window_size=window_size,
                                         gap=gap,
                                         where=None)


class SlidingStd(SlidingWindow):
    """
    Take std of data in each window defined by params
    """
    apply_to = [(variable_types.Numeric, variable_types.Numeric),
                (variable_types.Numeric, variable_types.Datetime)]
    _variable_type = variable_types.Numeric

    def __init__(self, base_feature, parent_entity, use_previous=None,
                 window_size=None, gap=None, where=None):
        function_name = "std"
        super(SlidingStd, self).__init__(function_name,
                                         base_feature,
                                         parent_entity,
                                         use_previous=use_previous,
                                         window_size=window_size,
                                         gap=gap,
                                         where=None)


def freq_time_unit(unit):
    PD_TIME_UNITS = {
        'd': 'D',
        's': 'S',
        'm': 'T',
        'h': 'H'
    }
    return PD_TIME_UNITS[unit]


def get_time_base(timestamp_end, timedelta, unit):
    ts_end = pd.Timestamp(timestamp_end)

    nanos_start_of_day = ts_end.normalize().value
    nanos_from_start_of_day = ts_end.value - nanos_start_of_day

    base = pd.Timedelta(nanos_from_start_of_day % timedelta.value, 'ns')
    base_in_units = base / np.timedelta64(1, unit)
    return base_in_units


def sampled_and_agg_observations(values, full_window, gap, rolling_func):
    if gap < 0:
        return c_utils.neg_gap(values.values, full_window, -gap, rolling_func)
    n = values.shape[0]
    overlapped_win = full_window + gap

    # reverse so we calculate groups backwards from end
    values_to_sample = values[::-1]
    groups = np.arange(0, n) / overlapped_win
    # reverse sort order while preserving groups
    groups = groups[-1] - groups
    values_to_sample = values_to_sample.to_frame("values")
    values_to_sample["groups"] = groups
    sampled = values_to_sample.groupby("groups")

    if gap > 0:
        def agg_func(df):
            # sort order preserved in pandas grouping
            if df.shape[0] > gap:
                df = df.iloc[:gap]
            return getattr(df, rolling_func)()
        return sampled["values"].agg(agg_func).values
    elif gap == 0:
        return getattr(sampled["values"], rolling_func)().values
