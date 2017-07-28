__author__ = 'jiyue'

from abc import ABCMeta, abstractmethod


class MainBootstrap(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def load_data_and_split(self,
                            split_mode='ratio',
                            in_format='dataframe',
                            in_postfix='csv'
                            ):
        pass

    @abstractmethod
    def go_binning(self, feature_list, target, event_identify, binning_mode, binning_spec_with, binned_other_value,
                   binned_num=5):
        pass

    @abstractmethod
    def train_score_card(self, feature_list, target, event_identify, feature_method='discrete', model='lr'):
        pass

    @abstractmethod
    def predict_score_card(self, feature_list, target):
        pass

    @abstractmethod
    def model_evaluation(self, score_col_name, target, event_identify, ks_bin_num=100):
        pass

    def go_bootstrap(self,
                     split_mode,
                     in_format,
                     in_postfix,
                     feature_list,
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
        self.load_data_and_split(split_mode, in_format, in_postfix)
