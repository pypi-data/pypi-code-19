# -*- coding:utf-8 -*-

import encoder
from sklearn.model_selection import cross_val_score
from sklearn.metrics import roc_curve, auc, roc_auc_score, accuracy_score

__author__ = 'jiyue'

import pandas as pd

df = pd.read_excel(
    '/home/jiyue/git/myproject/deeplearning/seven_online/risk_control/授信增信/待分箱数据.xls',
    sep='\t')

y = df['label']
x = df.drop(['label'], axis=1)

woeEncoder = encoder.WoeEncoder()
woeEncoder.fit_transform(x.values, y.values)
print woeEncoder._features_iv
print woeEncoder._binned_range
