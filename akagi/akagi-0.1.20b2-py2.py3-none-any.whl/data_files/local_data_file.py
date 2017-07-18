import os

from akagi.utils import gzip_decompress

from akagi.data_file import DataFile


class LocalDataFile(DataFile):
    def __init__(self, path, iterator_class):
        self.path = path
        self.iterator_class = iterator_class

    @property
    def filename(self):
        return os.path.basename(self.path)

    @property
    def raw_content(self):
        return open(self.path, 'rb')

    @property
    def key(self):
        return self.filename

    @property
    def content(self):
        if self._is_gzip():
            return gzip_decompress(self.raw_content)
        else:
            return self.iterator_class.open_file(self.path)
