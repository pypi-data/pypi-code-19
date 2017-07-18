import json
import os

from akagi.iterator import Iterator, FileFormat
from akagi.data_file_bundle import DataFileBundle
from akagi.data_files import LocalDataFile


class LocalDataFileBundle(DataFileBundle):
    def __init__(self, directory_path, file_format=FileFormat.CSV):
        self.directory_path = os.path.expanduser(directory_path)
        self._file_format = file_format
        self._iterator_class = None

    @property
    def data_files(self):
        paths = []

        for root, _, filenames in os.walk(self.directory_path):
            for filename in filenames:
                paths.append(os.path.join(root, filename))

        return [LocalDataFile(path, self.iterator_class) for path in paths]

    @property
    def iterator_class(self):
        if self._iterator_class is None:
            if 'iterator_class' in self.metadata:
                self._iterator_class = Iterator.get_iterator_class(self._file_format)
            else:
                self._iterator_class = Iterator.get_iterator_class(self._file_format)

        return self._iterator_class

    @property
    def metadata(self):
        if os.path.isfile(self._metadata_path):
            with open(self._metadata_path, 'r') as f:
                return json.load(f)
        else:
            return {}

    @property
    def _metadata_path(self):
        return os.path.dirname(self.directory_path) + '.json'

    def clear(self):
        # XXX: LocalDataFileBundle won't do anything on clear for local files safety.
        pass
