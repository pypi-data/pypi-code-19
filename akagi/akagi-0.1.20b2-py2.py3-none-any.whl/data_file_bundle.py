from itertools import chain
from abc import ABCMeta, abstractmethod, abstractproperty


class DataFileBundle(metaclass=ABCMeta):
    '''DataFileBundle is an base class of all data file bundles
    '''

    @abstractproperty
    def data_files(self):
        '''Retrieve the data files associated to the bundle.'''

    def __iter__(self):
        return iter(chain(*self.data_files))

    def __enter__(self):
        return self

    def __exit__(self, *exc_type):
        self.clear()
        return False

    @abstractmethod
    def clear(self):
        '''Clear associated datas.'''
