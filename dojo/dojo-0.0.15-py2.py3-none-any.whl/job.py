from __future__ import absolute_import, print_function, unicode_literals

import os


class Job(object):
    """A versioned job with an associated store for input and output storage"""

    def __init__(self, config, secrets):
        self.config = config
        self.secrets = secrets

    def run(self):
        raise NotImplementedError()

    def setup(self):
        self.store = self._build_store()
        self.store.setup()

    def teardown(self):
        self.store.teardown()

    def __enter__(self):
        self.setup()

    def __exit__(self, *args):
        self.teardown()

    def process(self, inputs):
        raise NotImplementedError()

    def input_paths(self):
        inputs = {}
        for input_name, input_config in self.config.get('inputs', {}).items():
            key = input_config.get('path', 'output-*')
            path = os.path.join('data', input_config['dataset'], '{{latest}}', key)
            inputs[input_name] = self._build_input_path(path)
        return inputs

    def output_path(self, prefix='data'):
        return os.path.join(prefix, self.config['name'], self.config['timestamp'])

    def output_schema(self):
        if 'schema' in self.config:
            return self.config['schema']
        return self.OUTPUT

    def _build_input_path(self, path):
        if '{{latest}}' in path:
            prefix_path = path.split('{{latest}}')[0]
            keys = self.store.list_keys(prefix_path)
            if len(keys) == 0:
                raise ValueError('{{latest}} requested in %s input path but no keys exist' % (path, ))
            last_key = keys[-1].strip('/').split('/')[-1]
            path = path.replace('{{latest}}', last_key)
        return path

    def _build_store(self):
        store_config = self.config['store']
        store_secrets = self.secrets['store']
        protocol = store_config['protocol']
        store_class = self.STORES[protocol]
        if protocol not in self.STORES:
            raise ValueError('dataset does not support protocol %s, only %s' % (protocol, ','.join(self.STORES)))
        return store_class(store_config, store_secrets, self)
