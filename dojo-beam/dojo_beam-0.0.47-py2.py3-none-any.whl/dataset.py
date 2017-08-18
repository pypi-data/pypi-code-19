from __future__ import absolute_import, print_function, unicode_literals

import apache_beam as beam

from dojo.dataset import Dataset

from .storage import BeamLocalFileStore, BeamGoogleStorageStore, BeamS3Store
from .transform import Conform, ConvertFrom, Validate
from .runners.direct import DirectBeamRunner
from .runners.dataflow import DataflowBeamRunner


class BeamDataset(Dataset):

    RUNNERS = {
        'direct': DirectBeamRunner,
        'cloud': DataflowBeamRunner
    }

    STORES = {
        'file': BeamLocalFileStore,
        'gs': BeamGoogleStorageStore,
        's3': BeamS3Store
    }

    def run(self, pipeline):
        self.pipeline = pipeline
        inputs = self.inputs()
        rows = self.process(inputs)
        self.output(rows)
        return rows

    def read_input(self, rows, dataset_name):
        schema = self.input_schema(dataset_name)
        return (rows | 'from_json ' + dataset_name >> beam.ParDo(ConvertFrom())
                     | 'validate ' + dataset_name >> beam.ParDo(Validate(schema)))

    def write_output(self, rows, format):
        # The storage class is expected to do the ConvertTo transform.
        return (rows | 'conform ' >> beam.ParDo(Conform(self.output_schema()))
                     | 'validate ' >> beam.ParDo(Validate(self.output_schema())))
