from __future__ import absolute_import, print_function, unicode_literals


class Storage(object):

    def __init__(self, config, secrets, dataset):
        self.config = config
        self.secrets = secrets
        self.dataset = dataset

    def read(self, path):
        raise NotImplementedError()

    def write(self, path, rows, format='json'):
        raise NotImplementedError()

    def as_uri(self, path):
        raise NotImplementedError()

    def setup(self):
        pass

    def teardown(self):
        pass

    def __enter__(self):
        self.setup()

    def __exit__(self, *args):
        self.teardown()
