# -*- coding: utf-8 -*-

from .context import mdspy

import unittest
import numpy as np

reload(mdspy.anomaly_detection)


class AnomalyDetectionTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_moving_average(self):
        output = {'distance': 17.666918237202548, 'prediction': 0.15, 'range': 0.048112522432468816}
        self.assertEqual(mdspy.anomaly_detection.moving_average([0.15, 0.1, 0.15, 0.2, 0.1], 1., ma=3, h=3), output)

    def test_single_exponential(self):
        output_1 = {'distance': 14.087944, 'prediction': 0.124555, 'range': 0.062141}
        self.assertEqual(
            mdspy.anomaly_detection.single_exponential_smoothing([0.15, 0.1, 0.15, 0.2, 0.1], 1., alpha=0.7, h=3),
            output_1)
        output_2 = {'distance': 12.727922, 'prediction': 0.1, 'range': 0.070711}
        self.assertEqual(
            mdspy.anomaly_detection.single_exponential_smoothing([0.15, 0.1, 0.15, 0.2, 0.1], 1., alpha=1., h=3),
            output_2)
        # test from Section 6.4.3.1 Single Exponential Smoothing, of NIST/SEMATECH e-Handbook of Statistical Methods
        # (see documentation)
        input = [71, 70, 69, 68, 64, 65, 72, 78, 75, 75, 75, 70]
        pred_ref = [np.nan, 71, 70.9, 70.71, 70.44, 69.8, 69.32, 69.58, 70.43, 70.88, 71.29, 71.67]
        pred = [np.nan, 71]
        for i in range(2, 11):
            pred.append(round(mdspy.anomaly_detection.single_exponential_smoothing(input[:i], input[i + 1],
                                                                                   alpha=0.1, h=1)['prediction'], 2))
        pred.append(round(mdspy.anomaly_detection.single_exponential_smoothing(input[:-1], input[-1],
                                                                               alpha=0.1, h=1)['prediction'], 2))
        self.assertEqual(pred_ref, pred)

    def test_double_exponential(self):
        # test from Section 6.4.3.4 Forecasting with Exponential Smoothing, of NIST/SEMATECH e-Handbook of Statistical
        # Methods (see documentation)
        input = np.array([6.4, 5.6, 7.8, 8.8, 11., 11.6, 16.7, 15.3, 21.6, 22.4])
        pred_ref = [np.nan, np.nan, np.nan, np.nan, 9.1, 11.4, 13.2, 17.4, 18.9, 23.1]
        pred = [np.nan, np.nan, np.nan, np.nan]
        for i in range(4, 10):
            pred.append(round(mdspy.anomaly_detection.double_exponential_smoothing(input[:i], input[i],
                                                                                   0.3623, 1., h=1)['prediction'], 1))
        self.assertEqual(pred_ref, pred)

    if __name__ == '__main__':
        unittest.main()
