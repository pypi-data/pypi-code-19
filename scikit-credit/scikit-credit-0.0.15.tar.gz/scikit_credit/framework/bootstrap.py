# -*- coding:utf-8 -*-
import collections
import encoder
from estimator import LRWrapper, XgBoostWrapper
from utils import common

__author__ = 'jiyue'

from sklearn.metrics import confusion_matrix
from sklearn.metrics import recall_score, precision_score, accuracy_score, roc_auc_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, cross_val_score, train_test_split, cross_val_predict, StratifiedKFold, \
    KFold
from sklearn.metrics import recall_score, precision_score, accuracy_score, roc_auc_score
from sklearn.dummy import DummyClassifier
from sklearn.metrics import roc_curve, auc, roc_auc_score, accuracy_score
from sklearn.linear_model import LogisticRegression

from abc import ABCMeta, abstractmethod
import pandas as pd


class Bootstrap(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.X_src = None
        self.y_src = None
        self.X_featured = None

    @abstractmethod
    def load_data(self,
                  file_path,
                  fea_list,
                  target,
                  split_mode='ratio',
                  in_format='dataframe',
                  in_postfix='csv'
                  ):
        pass

    @abstractmethod
    def go_binning(self, event_identify, binning_spec_with, binned_other_value,
                   binned_width=5, binning_mode='ef'):
        pass

    @abstractmethod
    def do_train(self, params, model='lr'):
        pass

    @abstractmethod
    def train_score_card(self, feature_list, target, feature_weights_file_path, feature_data_file, output_score_file,
                         sep=','):
        pass

    @abstractmethod
    def predict_score_card(self, target):
        pass

    @abstractmethod
    def model_evaluation(self, score_col_name, target, event_identify, ks_bin_num=100):
        pass

    def go_bootstrap(self,
                     file_path,
                     split_mode,
                     in_format,
                     in_postfix,
                     fea_list,
                     target,
                     event_identify,
                     binning_mode,
                     binning_spec_with,
                     binned_other_value,
                     binned_num,
                     feature_method,
                     model,
                     score_col_name,
                     ks_bin_num):
        self.load_data(file_path, fea_list, target, split_mode, in_format, in_postfix)
        self.go_binning(event_identify, binning_mode, binning_spec_with, binned_other_value,
                        binned_num)
        self.train_score_card(target, event_identify, feature_method, model)
        self.predict_score_card(target)
        self.model_evaluation(score_col_name, target, event_identify, ks_bin_num)


class MainBootstrap(Bootstrap):
    def __init__(self):
        super(MainBootstrap, self).__init__()
        self.binned_X = None
        self.woe = None
        self.df_binned_dummy_x = None
        self.weight_of_feature = None
        self.fea_list = None
        self.binned_range = None
        self.x_train = None
        self.x_test = None
        self.y_train = None
        self.y_test = None
        self.estimator = None

    def load_data(self,
                  file_path,
                  fea_list=None,
                  target='label',
                  split_mode='ratio',
                  in_format='dataframe',
                  in_postfix='csv'
                  ):
        data_frame = pd.DataFrame()
        if in_format == 'dataframe' and in_postfix == 'csv':
            data_frame = pd.read_csv(file_path)
        elif in_format == 'dataframe' and in_postfix == 'xls':
            data_frame = pd.read_excel(file_path)
        else:
            data0, data1 = common.load_svm_format_file(file_path)

        self.y_src = data_frame[target]
        if fea_list:
            self.X_src = data_frame.drop([target], axis=1).loc[:fea_list]
        else:
            self.X_src = data_frame.drop([target], axis=1)
        self.fea_list = self.X_src.columns.values.tolist()

    def _do_featuring(self):
        df_binned_x = pd.DataFrame(data=self.binned_X, columns=self.X_src.columns.values)
        for col in self.X_src.columns.values.tolist():
            df_binned_x[col] = df_binned_x[col].astype('category')
        self.df_binned_dummy_x = pd.get_dummies(df_binned_x)

    def go_binning(self, event_identify, binning_spec_with, binned_other_value,
                   binned_width=5, binning_mode='ef'):
        woe_encoder = encoder.WoeEncoder(binning_mode=binning_mode, bin_width=binned_width)
        woe_encoder.fit_transform(self.X_src.values, self.y_src.values)
        self.binned_X = woe_encoder._X_binned
        self.woe = woe_encoder._woe
        self.binned_range = woe_encoder._binned_range
        self._do_featuring()

    def do_train(self, params, model='lr'):
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.df_binned_dummy_x.values,
                                                                                self.y_src, test_size=0.3)
        if model == 'lr':
            self.estimator = LRWrapper(params)
        else:
            self.estimator = XgBoostWrapper(params)

        dummy_classifier = DummyClassifier(random_state=0, strategy='uniform')  # 基线模型
        dummy_classifier.fit(self.x_train, self.y_train)
        self.estimator.do_train(self.x_train, self.y_train)

    def do_predict(self):
        if not self.estimator:
            raise Exception(u'预测前必须先训练模型')
        pred, pred_proba = self.estimator.do_predict(self.x_test)
        return pred, pred_proba

    def get_column_name(self, column):
        column_arr = column.split('_')
        num = str(column_arr[len(column_arr) - 1])
        return column[:-len(num) - 1]

    def output_features_weight(self, path='/home/jiyue/Desktop/output_encoding'):
        columns = self.df_binned_dummy_x.columns.values
        with open(path, 'w') as f:
            index = 0
            f.write('feature\tweight\twoe\n')
            for fea_idx, features_list in enumerate(self.binned_range):
                for binned_index, feature_item_range in enumerate(features_list):
                    col_name = self.get_column_name(columns[index])
                    f.write(col_name + '$' + str(int(feature_item_range[0]))
                            + '~' + str(int(feature_item_range[1]))
                            + '\t' + str(self.estimator.weight_of_features[index])
                            + '\t' + str(self.woe[binned_index][fea_idx])
                            + '\n')
                    index += 1

    def train_score_card(self, feature_list, target,
                         feature_weights_file_path, feature_data_file, output_score_file,
                         sep=','):
        df = pd.read_csv(feature_data_file, sep=sep)
        with open(output_score_file, 'w') as f:
            feature_list.append('label')
            feature_list.append('prob')
            feature_list.append('zengxin_score')
            feature_list_str = ' '.join(feature_list)
            f.write(feature_list_str + '\n')

            for index, item in df.iterrows():
                sample = collections.OrderedDict()
                for feature in feature_list:
                    if feature in ('prob', 'zengxin_score'):
                        continue
                    sample[feature] = item[feature]
                common.cal_user_query_score(feature_weights_file_path, f, sample)

    def model_evaluation(self, score_col_name, target, event_identify, ks_bin_num=100):
        pass

    def predict_score_card(self, target):
        pass
