import logging
import sys
import traceback

class Log:
    NAME = __name__
    FORMAT_INFO = '%(message)s'
    FORMAT_DEBUG = '[%(levelname)s][%(module)s.%(funcName)s] %(message)s'

    logging.basicConfig(stream = sys.stdout, level = logging.INFO)

    for handler in logging.root.handlers:
        handler.addFilter(logging.Filter(NAME))

    logger = logging.getLogger(NAME)

    def __init__(self):
        pass

    @staticmethod
    def set_level(level):
        logformat = None

        if level == logging.DEBUG:
            logformat = Log.FORMAT_DEBUG
        else:
            logformat = Log.FORMAT_INFO

        for handler in logging.root.handlers:
            handler.setFormatter(logging.Formatter(logformat))

        Log.logger.setLevel(level)

    @staticmethod
    def traceback(logger, e):
        formatted_lines = traceback.format_exc().splitlines()
        for l in formatted_lines:
            logger.debug(l)
