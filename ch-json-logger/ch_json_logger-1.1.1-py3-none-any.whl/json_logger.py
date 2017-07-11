import logging
from json_log_formatter import JSONFormatter
from uuid import uuid4
import os
from logging.handlers import WatchedFileHandler

ERROR = "ERROR"
DEBUG = "DEBUG"
CRITICAL = "CRITICAL"
INFO = "INFO"
WARNING = "WARNING"


class JsonLogger:
    def __init__(self, log_path=None, name='json_logger'):
        self.uuid = str(uuid4())
        self.formatter = JSONFormatter()
        if log_path:
            self.log_path = log_path
        else:
            self.log_path = str(os.getcwd()) + '/logs/'

        error_handler = WatchedFileHandler(filename=self.log_path + 'error.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(self.formatter)

        self.logger = logging.getLogger(name)
        self.logger.addHandler(error_handler)

        info_handler = WatchedFileHandler(filename=self.log_path + 'info.log')
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(self.formatter)

        default_handler = logging.StreamHandler()
        default_handler.setLevel(logging.DEBUG)

        self.logger.addHandler(default_handler)

    def warning(self, message, params=None):
        if not params:
            params = {}
        params["log_id"] = self.uuid
        params["level"] = WARNING
        self.logger.warning(message, extra=params)

    def error(self, message, params=None):
        if not params:
            params = {}
        params["log_id"] = self.uuid
        params["level"] = ERROR
        self.logger.error(message, extra=params)

    def info(self, message, params=None):
        if not params:
            params = {}
        params["log_id"] = self.uuid
        params["level"] = INFO
        self.logger.info(message, extra=params)

    def critical(self, message, params=None):
        if not params:
            params = {}
        params["log_id"] = self.uuid
        params["level"] = CRITICAL
        self.logger.critical(message, extra=params)

    def debug(self, message, params=None):
        if not params:
            params = {}
        params["log_id"] = self.uuid
        params["level"] = DEBUG
        self.logger.debug(message, extra=params)
