# -*- coding:utf-8 -*-
import math
from sklearn.base import TransformerMixin
from sklearn.utils.multiclass import type_of_target
import numpy as np
from scipy import stats
import pandas as pd

__author__ = 'jiyue'


class WoeEncoder(TransformerMixin):
    def __init__(self,
                 binning_mode='ew',
                 bin_width=5,
                 bin_cols=None,
                 woe_min=-20,
                 woe_max=20,
                 binned_spec_width=None,
                 exclude_col=None
                 ):
        self._binning_mode = binning_mode
        self._bin_width = bin_width
        self._bin_cols = bin_cols
        self._WOE_MIN = woe_min
        self._WOE_MAX = woe_max
        self._features_woe = None
        self._features_iv = None
        self._X_binned = None
        self._woe = None
        self._binned_range = list()
        self._binned_spec_width = binned_spec_width

    def _check_target_type(self, y):
        type_y = type_of_target(y)
        if type_y not in ['binary']:
            raise ValueError('y must be binary variable')

    def _count_binary(self, x, event=1):
        event_count = (x == event).sum()
        non_event_count = x.shape[-1] - event_count
        return event_count, non_event_count

    def _compute_woe_iv(self, x, y, event=1):
        self._check_target_type(y)
        event_count, non_event_count = self._count_binary(y, event)
        x_labels = np.unique(x)
        woe_dict = dict()
        iv = 0
        for x1 in x_labels:
            y1 = y[np.where(x == x1)[0]]
            event_count_infeature, non_event_count_infeature = self._count_binary(y1, event)
            rate_event = 1.0 * event_count_infeature / event_count
            rate_non_event = 1.0 * non_event_count_infeature / non_event_count

            if rate_event == 0:
                woe1 = self._WOE_MIN
            elif rate_non_event == 0:
                woe1 = self._WOE_MAX
            else:
                woe1 = math.log(rate_event / rate_non_event)
            woe_dict[x1] = woe1
            iv += (rate_event - rate_non_event) * woe1
        return woe_dict, iv

    def _woe_compute(self, X, y, event=1):
        self._check_target_type(y)
        self._do_binning(X)

        tmp_features_woe = list()
        tmp_features_iv = list()
        for i in range(self._X_binned.shape[-1]):
            x = self._X_binned[:, i]
            woe_dict, iv = self._compute_woe_iv(x, y, event)
            tmp_features_woe.append(woe_dict)
            tmp_features_iv.append(iv)
        self._features_woe = np.array(tmp_features_woe)
        self._features_iv = np.array(tmp_features_iv)

    def eq_freq_binning(self, X, index_X):
        res = np.array([1] * X.shape[-1], dtype=int)
        bining_range = list()
        bin_index = 0
        q = 100 / self._bin_width
        binned_categories = pd.qcut(X, q, duplicates='drop')
        interval_list = binned_categories.categories.values.tolist()

        for interval in interval_list:
            left_point = round(interval.left, 3)
            right_point = round(interval.right, 3)

            X1 = X[np.where((X >= left_point) & (X < right_point))]
            mask = np.in1d(X, X1)
            res[mask] = bin_index + 1
            bin_index += 1
            bining_range.append([left_point, right_point])
        return res, bining_range

    def eq_width_binning2(self, X, index_X):
        res = np.array([1] * X.shape[-1], dtype=int)
        bining_range = list()
        bin_index = 0
        binned_categories = pd.cut(X, bins=self._bin_width)
        interval_list = binned_categories.categories.values.tolist()

        for interval in interval_list:
            left_point = int(math.ceil(interval.left))
            right_point = int(math.ceil(interval.right))

            X1 = X[np.where((X >= left_point) & (X < right_point))]
            mask = np.in1d(X, X1)
            res[mask] = bin_index + 1
            bin_index += 1
            bining_range.append([left_point, right_point])
        return res, bining_range

    # 这里实现等宽分箱
    def eq_width_binning(self, X, index_X):
        res = np.array([1] * X.shape[-1], dtype=int)
        bining_range = list()
        bin_index = 0
        if not self._binned_spec_width:
            percentile = 100 / self._bin_width
        else:
            percentile = 100 / self._binned_spec_width[index_X]

        i = 0
        flag = False
        X_target = X

        while True and i < self._bin_width:
            left_point = stats.scoreatpercentile(X_target, i * percentile)
            right_point = stats.scoreatpercentile(X_target, (i + 1) * percentile)
            i += 1
            if left_point == right_point and left_point == 0:
                flag = False
                continue

            if not flag:
                X_target = X[np.where(X >= right_point)]
                flag = True
                i = 0
                X1 = X[np.where((X >= left_point) & (X < right_point))]
                mask = np.in1d(X, X1)
                res[mask] = bin_index + 1
                bin_index += 1
                print np.unique(res)
                bining_range.append([left_point, right_point])
                continue

            X1 = X[np.where((X >= left_point) & (X < right_point))]
            mask = np.in1d(X, X1)
            res[mask] = bin_index + 1
            bin_index += 1
            print np.unique(res)
            bining_range.append([left_point, right_point])
        return res, bining_range

    def _do_smooth(self, X, i):
        if self._binning_mode == 'ew':  # 等宽分箱
            return self.eq_width_binning2(X, i)
        else:  # 等频分箱
            return self.eq_freq_binning(X, i)

    def _do_binning(self, X):
        tmp = list()
        for i in range(X.shape[-1]):
            x = X[:, i]
            x_discrete, bining_range = self._do_smooth(x, i)
            tmp.append(x_discrete)
            self._binned_range.append(bining_range)
        self._X_binned = np.array(tmp).T

    def _convert_to_woe(self, X_binned, woe_arr):
        if X_binned.shape[-1] != woe_arr.shape[-1]:
            raise ValueError('dimension is not consistence')
        self._woe = np.copy(X_binned).astype(float)
        idx = 0
        for woe_dict in woe_arr:
            for k in woe_dict.keys():
                woe = woe_dict[k]
                self._woe[:, idx][np.where(self._woe[:, idx] == k)[0]] = woe * 1.0
            idx += 1
        return self._woe

    def fit(self, X, y):
        self._woe_compute(X, y)
        return self

    def transform(self, X):
        return self._convert_to_woe(self._X_binned, self._features_woe)
