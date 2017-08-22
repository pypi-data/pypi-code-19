# coding=utf-8
import pandas as pd
import datetime
from scipy import stats
import numpy as np


def ttt_ratio(ts, target):
    """
    Performs the time to target using the sum of deltas. This approach is similar to calculate the ratio considering
    the first and last point.

    TODO: - This implementation is not considering "recharged"

    TODO: - This implementation doesn't remove outliers

    TODO: - This implementation doesn't trait corner cases (example: slope == 0)

    Parameters
    ----------
    ts : Series
        pandas Series used in the training process
    target : number
        The target

    Returns
    -------
    time_to_target : float
        The number of days predicted to reach the target

    References
    ----------

    Examples
    --------
    >>> ts_test = pd.Series(
    >>>     index=pd.to_datetime(['2017-01-01', '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05']),
    >>>     data=[10, 5, 10, 5, 4])
    >>> target = 0
    >>> mdspy.ttt.ttt_ratio(ts_test, target)
    2.666666666
    """
    diffs = sum(ts.diff(1).fillna(0.0))
    delta = ts.tail(1).index[0] - ts.head(1).index[0]
    delta_days = delta.days
    last_value = ts.tail(1).values[0]
    ratio = abs(diffs / delta_days)
    return (last_value - target) / ratio


def ttt_ratio_ma(ts, target, w):
    """
    Initially smooth the time series applying a moving average. After, performs the time to target using the sum of
    deltas. This approach is similar to calculate the ratio considering the first and last point.
    The same as ttt_ratio but with a moving average smooth.

    TODO: - This implementation is not considering "recharged"

    TODO: - This implementation doesn't remove outliers

    TODO: - This implementation doesn't trait corner cases (example: slope == 0)

    Parameters
    ----------
    ts : Series
        pandas Series used in the training process
    target : number
        The target
    w : int
        Size of window to smooth the time series

    Returns
    -------
    time_to_target : float
        The number of days predicted to reach the target

    References
    ----------

    Examples
    --------
    >>> ts_test = pd.Series(
    >>>     index=pd.to_datetime(['2017-01-01', '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05']),
    >>>     data=[10, 5, 10, 5, 4])
    >>> target = 0
    >>> window = 2
    >>> mdspy.ttt.ttt_ratio_ma(ts_test, target, window)
    5.3333333
    """
    diffs = sum(ts.rolling(window=w).mean().diff(1).fillna(0.0))
    delta = ts.tail(1).index[0] - ts.head(1).index[0]
    delta_days = delta.days
    initial = ts.tail(1).values[0]
    ratio = abs(diffs / delta_days)
    return (initial - target) / ratio


def ttt_linear_regression(ts, target):
    """
    Performs a linear regression and use the slope to calculate the time to target.

    TODO: - This implementation is not considering "recharged"

    TODO: - This implementation doesn't remove outliers

    TODO: - This implementation doesn't trait corner cases (example: slope == 0)

    Parameters
    ----------
    ts : Series
        pandas Series used in the training process
    target : number
        The target

    Returns
    -------
    time_to_target : float
        The number of days predicted to reach the target

    References
    ----------

    Examples
    --------
    >>> ts_test = pd.Series(
    >>>     index=pd.to_datetime(['2017-01-01', '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05']),
    >>>     data=[10, 5, 10, 5, 4])
    >>> target = 0
    >>> mdspy.ttt.ttt_linear_regression(ts_test, target)
    3.3333333
    """
    epoch = ts.index.astype(np.int64) / 1000000000
    slope, intercept, r_value, p_value, std_err = stats.linregress(epoch, ts.values)
    prediction = ((target - ts.tail(1).values[0])/slope) / (60.0 * 60.0 * 24.0)
    return prediction
