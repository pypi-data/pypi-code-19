from sklearn.linear_model import LogisticRegression
from estimator.main_wrap import MainWrapper
import pandas as pd

__author__ = 'jiyue'


class LRWrapper(MainWrapper):
    def __init__(self, params):
        super(LRWrapper, self).__init__(params)
        self.lr = None
        self.coef = None

    def do_train(self, x_train, y_train, x_test=None, y_test=None):
        self.lr = LogisticRegression(**self.params)
        self.lr.fit(x_train, y_train)
        self.coef = self.lr.coef_[0]
        self.weight_of_features = self.coef

    def do_predict(self, x_test, y_test=None, x_train=None, y_train=None):
        rf_predict = self.lr.predict(x_test)
        rf_predict_proba = self.lr.predict_proba(x_test)[:, 1]
        return rf_predict, rf_predict_proba

    def output_weight(self, fea_list):
        self.weight_of_features = self.coef
