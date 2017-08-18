from __future__ import absolute_import, print_function, unicode_literals

from .stores.local_file import VanillaLocalFileStore
from .stores.google_storage import VanillaGoogleStorage
from .stores.s3 import VanillaS3Store
from ..dataset import Dataset
from ..transforms import Conform, ConvertFrom, Validate
from ..runners.job import JobRunner


class VanillaDataset(Dataset):

    RUNNERS = {
        'direct': JobRunner
    }

    STORES = {
        'file': VanillaLocalFileStore,
        'gs': VanillaGoogleStorage,
        's3': VanillaS3Store
    }

    def read_input(self, rows, dataset_name):
        rows = filter(lambda row: row, rows)
        rows = map(ConvertFrom().process, rows)
        schema = self.input_schema(dataset_name)
        rows = map(Validate(schema).process, rows)
        return rows

    def write_output(self, rows, format):
        rows = map(Conform(self.output_schema()).process, rows)
        rows = map(Validate(self.output_schema()).process, rows)
        # The storage class is expected to do the ConvertTo transform.
        return rows
