import csv
from six import StringIO, BytesIO
import six


class CSVIterator(object):
    def __init__(self, content, skip_errors=True):
        self.content = self.decode(content)
        self._skip_errors = skip_errors
        self._iterator = None

    @classmethod
    def open_file(cls, path):
        return open(path, newline='')

    def decode(self, content):
        if six.PY2:
            return content
        else:
            if type(content) == BytesIO:
                return StringIO(content.decode('utf-8')).read()
            else:
                return content

    def __next__(self):
        try:
            n = self._iterator.__next__()
            return n
        except StopIteration as e:
            raise e
        except Exception as e:
            if self._skip_errors:
                return self._iterator.__next__()
            else:
                raise e

    def __iter__(self):
        self._iterator = csv.reader(self.content, escapechar='\\')
        return self
