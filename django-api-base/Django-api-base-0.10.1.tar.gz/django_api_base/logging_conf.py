import logging


class Logger(object):

    def __init__(self):
        self.logger_info = logging.getLogger('info')
        self.logger_error = logging.getLogger('error')
        self.logger_debug = logging.getLogger('debug')
        super(Logger, self).__init__()

    def info(self, msg):
        self.logger_info.info(msg)

    def error(self, msg):
        self.logger_error.error(msg)

    def debug(self, msg):
        self.logger_debug.debug(msg)
