import csv
from six import StringIO
import six
import io


class CSVIterator(object):
    def __init__(self, content, skip_errors=True):
        self.content = self.decode(content)
        self._skip_errors = skip_errors
        self._iterator = csv.reader(self.content, escapechar='\\')

    @classmethod
    def open_file(cls, path):
        return open(path, newline='')

    def decode(self, content):
        if six.PY2:
            return content
        else:
            if isinstance(content, io.TextIOBase):
                return content
            else:
                return StringIO(content.decode('utf-8'))

    def __next__(self):
        try:
            return next(self._iterator)
        except StopIteration as e:
            raise e
        except Exception as e:
            if self._skip_errors:
                return next(self._iterator)
            else:
                raise e
