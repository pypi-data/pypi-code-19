from abc import ABCMeta, abstractmethod, abstractproperty


class DataFileBundle(metaclass=ABCMeta):
    '''DataFileBundle is an base class of all data file bundles
    '''

    @abstractproperty
    def data_files(self):
        '''Retrieve the data files associated to the bundle.'''

    def __iter__(self):
        for i, df in enumerate(self.data_files):
            # XXX: cache here (S3DataFile => LocalDataFile)

            it = iter(df)
            while True:
                try:
                    yield next(it)
                except StopIteration as e:
                    break

    def __enter__(self):
        return self

    def __exit__(self, *exc_type):
        self.clear()
        return False

    @abstractmethod
    def clear(self):
        '''Clear associated datas.'''
