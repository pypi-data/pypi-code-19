from operator import itemgetter
import operator
import pandas as pd
import numpy as np
from estimator.main_wrap import MainWrapper
import xgboost as xgb
import sys

__author__ = 'jiyue'


class XgBoostWrapper(MainWrapper):
    def __init__(self, params):
        super(XgBoostWrapper, self).__init__(params)
        self.imp = None
        self.gbm = None

    def create_feature_map(self, fea_list, fmap_file='xgb.fmap'):
        outfile = open(fmap_file, 'w')
        for i, feat in enumerate(self, fea_list):
            outfile.write('{0}\t{1}\tq\n'.format(i, feat))
        outfile.close()

    def get_importance(self, features):
        self.create_feature_map(features)
        importance = self.gbm.get_fscore(fmap='xgb.fmap')
        importance = sorted(importance.items(), key=itemgetter(1), reverse=True)
        self.imp = importance

    def print_features_importance(self):
        for i in range(len(self.imp)):
            print("# " + str(self.imp[i][1]))
            print('output.remove(\'' + self.imp[i][0] + '\')')

    def do_train(self, x_train, y_train, x_test=None, y_test=None):
        xgtrain = xgb.DMatrix(x_train, label=y_train, missing=np.nan)
        xgtest = xgb.DMatrix(x_test, label=y_test, missing=np.nan)

        evallist = [(xgtrain, 'train'), (xgtest, 'eval')]
        self.gbm = xgb.train(self.params, xgtrain, self.params['num_round'], evallist,
                             early_stopping_rounds=10)
        self.gbm.save_model('tree.model')
        self.gbm.dump_model('tree.model.explain')
        fscore = sorted(self.gbm.get_fscore().items(), key=lambda x: x[1], reverse=True)

    def do_predict(self, x_test, y_test, x_train=None, y_train=None):
        xgtrain = xgb.DMatrix(x_test, label=y_test, missing=np.nan)
        bst = xgb.Booster({'nthread': 4})
        bst.load_model('tree.model')
        preds = bst.predict(xgtrain)
        return preds

    def output_weight(self, fea_list):
        self.create_feature_map(fea_list)
        importance = self.gbm.get_fscore(fmap='xgb.fmap')
        importance = sorted(importance.items(), key=operator.itemgetter(1))
        df = pd.DataFrame(importance, columns=['feature', 'fscore'])
        df['fscore'] = df['fscore'] / df['fscore'].sum()
        self.weight_of_features = df
