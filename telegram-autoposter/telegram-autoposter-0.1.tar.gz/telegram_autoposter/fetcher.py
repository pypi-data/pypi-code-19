import logging


class Fetcher(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch(self, *args, **kwargs):
        raise NotImplemented('Must overwrite ::fetch method.')
