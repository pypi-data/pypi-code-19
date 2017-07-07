import logging
from json_log_formatter import JSONFormatter
from uuid import uuid4

ERROR = "ERROR"
DEBUG = "DEBUG"
CRITICAL = "CRITICAL"
INFO = "INFO"
WARNING = "WARNING"


class JsonLogger:
    def __init__(self, log_name):
        self.uuid = str(uuid4())
        formatter = JSONFormatter()

        self.json_handler = logging.FileHandler(filename=log_name + ".logs")
        self.json_handler.setFormatter(formatter)

        self.logger = logging.getLogger('my_json')
        self.logger.addHandler(self.json_handler)
        self.logger.setLevel(logging.DEBUG)

    def __del__(self):
        self.logger.removeHandler(self.json_handler)
        del self.logger
        del self.json_handler

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
