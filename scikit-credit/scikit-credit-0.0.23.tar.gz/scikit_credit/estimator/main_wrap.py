__author__ = 'jiyue'
from abc import ABCMeta, abstractmethod


class MainWrapper(object):
    __metaclass__ = ABCMeta

    def __init__(self, params):
        self.params = params
        self.weight_of_features = None

    @abstractmethod
    def do_train(self, x_train, y_train, x_test=None, y_test=None):
        pass

    @abstractmethod
    def do_predict(self, x_test, y_test=None, x_train=None, y_train=None):
        pass

    @abstractmethod
    def output_weight(self, fea_list):
        pass
