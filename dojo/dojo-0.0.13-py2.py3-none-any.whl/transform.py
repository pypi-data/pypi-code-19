from __future__ import absolute_import, print_function, unicode_literals


class Transform(object):

    def __init__(self, config={}, secrets={}):
        self.config = config
        self.secrets = secrets

    def process(self, row):
        raise NotImplementedError()
