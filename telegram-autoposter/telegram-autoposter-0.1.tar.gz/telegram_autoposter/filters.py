import logging


class Filter(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def filter(self, data, *args, **kwargs):
        self.logger.debug('Filtering...')
        return data
