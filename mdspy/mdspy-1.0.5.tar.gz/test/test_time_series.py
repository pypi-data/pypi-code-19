# -*- coding: utf-8 -*-

from .context import mdspy

import unittest

reload(mdspy.time_series)


class TimeSeriesTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_decompose(self):
        from statsmodels.tsa.seasonal import seasonal_decompose
        import numpy as np

        angles = np.arange(1000) * 2 * 4 * np.pi / 1000
        noise = np.random.normal(0, .05, 1000)
        signal = angles + noise
        trend = np.arange(1000) / 500
        signal = trend + angles

        decomp = mdspy.time_series.decompose(signal, freq=200)
        ref = seasonal_decompose(signal, freq=200)

        np.testing.assert_array_equal(decomp.trend, ref.trend)
        np.testing.assert_array_equal(decomp.seasonal, ref.seasonal)
        np.testing.assert_array_equal(decomp.resid, ref.resid)


if __name__ == '__main__':
    unittest.main()
