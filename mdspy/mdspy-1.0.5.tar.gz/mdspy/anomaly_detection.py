import numpy as np


def moving_average(series, sample, ma=20, h=30):
    """
        Predicts the value of the sample based on the average value calculated on the last values of the series.
        Computes the error between prediction and observation and normalizes with the RMSE of errors.

        Parameters
        ----------
        series : array_like
            Input time series
        sample : float
            Sample (observation) to compare the prediction to
        ma : int
            Size of the rolling window (default: 20 samples)
        h : int
            Size of the history (default: 30 samples)

        Returns
        -------
        dict
            `distance`: the distance, expressed in standard deviations of the history values \n
            `prediction`: the prediction for the last value of the input time series \n
            `range`: the standard deviation of of the errors in the history

        Notes
        -----
        The RMSE is calculated on the values of the history.
        The predictions are computed using a moving average long of the "ma" previous samples.
        Because of the normalization, the distance value is to be interpreted in RMSE unit.

        As a rule of thumb, an absolute distance lower than 1 or 2 is acceptable. An absolute value above would probably
        be the sign of an anomaly.

        References
        ----------

        Examples
        --------
        >>> mdspy.anomaly_detection.moving_average([0.15, 0.1, 0.15, 0.2, 0.1], 1., ma=3, h=3)
        {'distance': 17.666918237202548, 'prediction': 0.15, 'range': 0.048112522432468816}
    """

    assert isinstance(series, list)
    result = series[:ma]
    for i in range(ma, len(series)):
        result.append(np.mean(series[i - ma:i]))
    assert len(result) == len(series)
    result.append(np.mean(series[len(series) - ma:]))
    mse = []
    for i in range(len(series) - h, len(series)):
        mse.append(abs(series[i] - result[i]) ** 2)
    rmse = np.sqrt(np.mean(mse))
    output = {'distance': abs(sample - result[-1]) / rmse, 'prediction': result[-1], 'range': rmse}
    return output


def single_exponential_smoothing(series, sample, alpha=0.7, h=10):
    '''
        Predicts the value of the `sample` based on the exponential smoothing algorithm applied to the series of
        previous values.
        The prediction is also used to compute the error with the observation, normalized with the RMSE of previous
        errors.

        Parameters
        ----------
        series : array_like
            Input time series
        sample : float
            Sample (observation) to compare the prediction to
        alpha : float
            Weight (or smoothing factor) to assign to the previous sample
        h : int
            Size of the history (default: 10 samples)

        Returns
        -------
        dict
            `distance`: the distance, expressed in standard deviations of the history values \n
            `prediction`: the prediction for the last value of the input time series \n
            `range`: the standard deviation of of the errors in the history

        Notes
        -----
        The formula for computing the prediction is [1]_

        .. math::
            S_t = a * y_t + (1 - a) * S_{t-1}

        with :math:`S` being the estimate of :math:`y`, :math:`y` the observation and :math:`a` being the smoothing
        factor (or weight). Initialization is :math:`S_0 = y_0`.

        For the forecasting purpose, :math:`S_t` is considered as the prediction
        of the sample :math:`y_{t+1}`, computed with :math:`y_t` and :math:`S_{t-1}`.

        References
        ----------
        .. [1] Section 6.4.3.1 Single Exponential Smoothing. Based on NIST/SEMATECH e-Handbook of Statistical Methods
           http://www.itl.nist.gov/div898/handbook/pmc/section4/pmc431.htm

        Examples
        --------
        >>> mdspy.anomaly_detection.single_exponential_smoothing([0.15, 0.1, 0.15, 0.2, 0.1], 1., alpha=0.7, h=3)
        {'distance': 14.087944, 'prediction': 0.124555, 'range': 0.062141}
        >>> mdspy.anomaly_detection.single_exponential_smoothing([0.15, 0.1, 0.15, 0.2, 0.1], 1., alpha=1., h=3)
        {'distance': 12.727922, 'prediction': 0.1, 'range': 0.070711}
    '''

    assert isinstance(series, list)
    result = [np.nan, series[0]]
    for i in range(1, len(series)):
        result.append(alpha * series[i] + (1 - alpha) * result[i])
    assert len(result) == len(series) + 1
    mse = []
    assert len(series) - h >= 0
    for i in range(len(series) - h, len(series)):
        mse.append(abs(series[i] - result[i]) ** 2)
        # TODO why should we take the maximum between the squared error and 0.01 + where 0.01 comes from?
        # mse.append(max(abs(series[i] - result[i]) ** 2, 0.01))
    rmse = np.sqrt(np.mean(mse))
    output = {'distance': round(abs(sample - result[-1]) / rmse, 6), 'prediction': round(result[-1], 6),
              'range': round(rmse, 6)}
    return output


def double_exponential_smoothing(series, sample, alpha, beta, h=3):
    '''
        Predicts the value of the `sample` based on the exponential smoothing algorithm applied to the series of
        previous values.
        The prediction is also used to compute the error with the observation, normalized with the RMSE of previous
        errors.

        Parameters
        ----------
        series : array_like
            Input time series
        sample : float
            Sample (observation) to compare the prediction to
        alpha : float
            Weight (or smoothing factor) to assign to the previous sample
        beta : float
            Trend factor
        h : int
            Size of the history (default: 10 samples)

        Returns
        -------
        dict
            `distance`: the distance, expressed in standard deviations of the history values \n
            `prediction`: the prediction for the last value of the input time series \n
            `range`: the standard deviation of of the errors in the history

        Notes
        -----
        The system of two formulas used to compute the terms [1]_:

        .. math::
            S_t &= alpha * y_t + (1 - alpha) * (S_{t-1} + b_{t-1})

            b_t &= beta * (S_t - S_{t-1}) + (1 - beta) * b_{t-}1

        with `S` being the smoothed values, `b` the trend value, `y` the input series, alpha and beta the 2 required
        parameters and t the index.

        Initiation of S is often performed with S[1] = y[1]. Regarding b, 3 ways are suggested:

        .. math::
            b_1 &= y_2 - y_1

            b_1 &= 1/3 * ((y_2 - y_1) + (y_3 - y_2) + (y_4 - y_3))

            b_1 &= (y_n - y_1) / (n - 1)

        Forecasting is made with the following formula: :math:`F_{t+1} = S_t + b_t` [2]_

        References
        ----------
        .. [1] Section 6.4.3.3 Double Exponential Smoothing. Based on NIST/SEMATECH e-Handbook of Statistical Methods
           http://www.itl.nist.gov/div898/handbook/pmc/section4/pmc433.htm
        .. [2] Section 6.4.3.4 Forecasting with Double Exponential Smoothing (LASP). Based on NIST/SEMATECH e-Handbook
           of Statistical Methods http://www.itl.nist.gov/div898/handbook/pmc/section4/pmc434.htm

        Examples
        --------
        >>> y = [6.4, 5.6, 7.8, 8.8, 11., 11.6, 16.7, 15.3, 21.6]
        >>> sample = 22.4
        >>> mdspy.anomaly_detection.double_exponential_smoothing(y, sample, 0.3623, 1.0, h=3)
        {'distance': 0.228424, 'range': 2.849382, 'prediction': 23.050868}
    '''

    # result = [np.nan, series[0] + (series[1] - series[0])]
    result = [np.nan, series[0] + np.sum((series[1:4] - series[:3])) / 3]
    for n in range(1, len(series)):
        if n == 1:
            # level, trend = series[0], series[1] - series[0]
            level, trend = series[0], np.sum((series[1:4] - series[:3])) / 3
        if n >= len(series):
            value = result[-1]
        else:
            value = series[n]
        last_level, level = level, alpha * value + (1 - alpha) * (level + trend)
        trend = beta * (level - last_level) + (1 - beta) * trend
        result.append(level + trend)
    assert len(result) == len(series) + 1
    mse = []
    assert len(series) - h >= 0
    for i in range(len(series) - h, len(series)):
        mse.append(abs(series[i] - result[i]) ** 2)
    rmse = np.sqrt(np.mean(mse))
    output = {'distance': round(abs(sample - result[-1]) / rmse, 6), 'prediction': round(result[-1], 6),
              'range': round(rmse, 6)}
    return output
