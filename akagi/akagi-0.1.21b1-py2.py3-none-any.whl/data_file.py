import os
from abc import ABCMeta, abstractproperty


class DataFile(metaclass=ABCMeta):
    def __iter__(self):
        return self.iterator_class(self.content)

    def _is_gzip(self):
        return os.path.splitext(self.filename)[-1] == '.gz'

    @abstractproperty
    def filename(self):
        '''Retrieve filename'''

    @abstractproperty
    def key(self):
        '''Retrieve key (used in caching function)'''

    @abstractproperty
    def content(self):
        '''Content in data file.
        Compressed archives will be automatically decompressed.
        '''

    @property
    def raw_content(self):
        '''Raw content in data file'''
