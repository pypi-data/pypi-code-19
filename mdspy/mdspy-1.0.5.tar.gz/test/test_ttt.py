# -*- coding: utf-8 -*-

from .context import mdspy
import unittest
import pandas as pd

reload(mdspy.time_series)


class TTTTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_ttt_ratio(self):
        df_test = pd.Series(
            index=pd.to_datetime(['2017-01-01', '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05']),
            data=[10, 5, 10, 5, 4])
        target = 0
        self.assertAlmostEqual(2.66666666, mdspy.ttt.ttt_ratio(df_test, target))

    def test_ttt_ratio_ma(self):
        df_test = pd.Series(
            index=pd.to_datetime(['2017-01-01', '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05']),
            data=[10, 5, 10, 5, 4])
        target = 0
        self.assertAlmostEqual(5.3333333, mdspy.ttt.ttt_ratio_ma(df_test, target, 2))

    def test_ttt_linear_regression(self):
        df_test = pd.Series(
            index=pd.to_datetime(['2017-01-01', '2017-01-02', '2017-01-03', '2017-01-04', '2017-01-05']),
            data=[10, 5, 10, 5, 4])
        target = 0
        self.assertAlmostEqual(3.3333333, mdspy.ttt.ttt_linear_regression(df_test, target))


if __name__ == '__main__':
    unittest.main()
