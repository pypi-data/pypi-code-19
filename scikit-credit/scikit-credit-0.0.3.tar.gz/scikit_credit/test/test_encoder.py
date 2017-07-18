import encoder
from sklearn.model_selection import cross_val_score
from sklearn.metrics import roc_curve, auc,roc_auc_score,accuracy_score

__author__ = 'jiyue'

import pandas as pd

df = pd.read_csv(
    '/home/jiyue/git/myproject/deeplearning/scikit-credit/scikit-credit/scikit_credit/data/tmp_risk_modeling_slice.csv',
    sep='\t')

x = df.loc[:, ['max_overdue_days', 'orign_amount', 'order_num']]
y = df['label']
woeEncoder = encoder.WoeEncoder()
woeEncoder.fit_transform(x.values, y.values)


y_pred_score = df['sdsy_score']
y_test = df['label']

fpr, tpr, thresholds = roc_curve(y_true=y_test.values,y_score= y_pred_score.values)
