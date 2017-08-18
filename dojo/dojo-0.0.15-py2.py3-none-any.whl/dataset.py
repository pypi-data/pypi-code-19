from __future__ import absolute_import, print_function, unicode_literals

import os

from .job import Job


class Dataset(Job):
    """A versioned job with defined input and output schemas"""

    INPUTS = {}

    def __init__(self, *args, **kwargs):
        super(Dataset, self).__init__(*args, **kwargs)

        # Convert short-hand inputs to full full dict representation.
        if 'inputs' in self.config:
            if isinstance(self.config['inputs'], list):
                self.config['inputs'] = {key: {'dataset': key} for key in self.config['inputs']}
            for key, input_config in self.config['inputs'].items():
                if isinstance(input_config, str):
                    self.config['inputs'][key] = {'dataset': input_config}

    def run(self):
        inputs = self.inputs()
        rows = self.process(inputs)
        self.output(rows)
        return rows

    def process(self, inputs):
        raise NotImplementedError()

    def read_input(self, rows, dataset_name):
        raise NotImplementedError()

    def write_output(self, rows, format):
        raise NotImplementedError()

    def inputs(self):
        inputs = {}
        for input_name, input_path in self.input_paths().items():
            rows = self.store.read(input_path)
            dataset_name = self.config['inputs'][input_name]['dataset']
            inputs[input_name] = self.read_input(rows, dataset_name)
        return inputs

    def output(self, rows, format='json', key='output'):
        if rows is None:
            return
        format = self.config.get('format', format)
        rows = self.write_output(rows, format)
        output_path = os.path.join(self.output_path(), key)
        return self.store.write(output_path, rows, format=format)

    def input_schema(self, dataset_name):
        input_keys = {input_config['dataset']: key for key, input_config in self.config['inputs'].items()}
        return self.INPUTS[input_keys[dataset_name]]
