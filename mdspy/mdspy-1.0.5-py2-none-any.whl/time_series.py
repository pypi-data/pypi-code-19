from statsmodels.tsa.seasonal import seasonal_decompose

def decompose(series, model='additive', filt=None, freq=None):
    """
        Wrapper of the `seasonal_decompose` function of the statsmodels package. Quoting the statsmodels documentation,
        this function decomposes a time series using moving averages

        Parameters
        ----------
        series : array_like
            Input time series
        model : str {"additive", "multiplicative"}
            Type of seasonal component. Abbreviations are accepted.
        filt : array_like
            The filter coefficients for filtering out the seasonal component.
            The concrete moving average method used in filtering is determined by two_sided.
        freq : int, optional
            Frequency of the series. Must be used if x is not a pandas object.
            Overrides default periodicity of x if x is a pandas object with a timeseries index.

        Returns
        -------
        obj
            A object with seasonal, trend, and resid attributes.

        Notes
        -----
        For more details, see the documentation of statsmodels [1]_

        References
        ----------
        .. [1] Function seasonal_decompose() from statsmodels documentation
           http://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.seasonal_decompose.html

        Examples
        --------

        >>> import numpy as np
        >>> import matplotlib.pylab as plt
        >>>
        >>> angles = np.arange(1000) * 2 * 10 * np.pi / 1000
        >>> noise = np.random.normal(0, .05, 1000)
        >>> signal = np.sin(angles) + noise
        >>> trend = np.arange(1000.) / 500
        >>> signal = trend + signal
        >>>
        >>> decomp = sm.tsa.seasonal_decompose(signal, freq=200)
        >>> decomp.plot()
        >>> plt.show()
        <matplotlib.figure.Figure at 0x11cfd3a90>
    """
    decomp = seasonal_decompose(series, model=model, filt=filt, freq=freq)
    return decomp
