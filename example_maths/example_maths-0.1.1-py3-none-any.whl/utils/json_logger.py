'''logging utilities'''

import logging
import logging.config
from os import path

import pythonjsonlogger


logging.config.fileConfig(path.join(path.dirname(__file__), "logging.conf"))


def get_json_logger():
    '''returns json logger'''
    return logging.getLogger("custom")
