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
    def __init__(self, app):
        if app:
            self.uuid = str(uuid4())
            self.formatter = JSONFormatter()
            if app.config.get('LOG_PATH'):
                self.log_path = app.config.get('LOG_PATH')
            else:
                self.log_path = str(os.getcwd()) + '/logs/'

            error_handler = WatchedFileHandler(filename=self.log_path + 'error.log')
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(self.formatter)

            self.logger = logging.getLogger(app.name)
            self.logger.addHandler(error_handler)

            info_handler = WatchedFileHandler(filename=self.log_path + 'info.log')
            info_handler.setLevel(logging.INFO)
            info_handler.setFormatter(self.formatter)

            default_handler = logging.StreamHandler()
            default_handler.setLevel(logging.DEBUG)

            self.logger.addHandler(default_handler)
        raise ValueError('Invalid app have been received')

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
