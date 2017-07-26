# -*- coding: utf-8 -*-
"""
    logger
    ~~~~~~

    This is the logger configuration module for DOMI.

    :copyright: (c) 2016 by Cooperativa de Trabajo BITSON Ltda.
    :author: Leandro E. Colombo Viña.
    :license: GPL v3.0, see LICENSE for more details.

"""
# Standard lib imports
import logging.handlers
import time
import os
import sys
# Third Party imports
from rainbow_logging_handler import RainbowLoggingHandler
# BITSON imports
# from config import Config

console_logger = logging.getLogger('domi')
console_logger.setLevel(logging.DEBUG)

console_handler = RainbowLoggingHandler(sys.stderr)
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(fmt="%(message)s"))

console_logger.addHandler(console_handler)

log_format = "".join(["[%(asctime)s] %(name)20s - %(levelname)8s: ",
                          "%(threadName)15s-%(funcName)15s() - %(message)s"])
formatter = logging.Formatter(fmt=log_format)
# Format UTC Time
formatter.converter = time.gmtime
# logfile = os.path.join(Config.LOG_FOLDER,
#                        '{}.log'.format(Config.PROJECT_NAME))
#
# file_handler = logging.handlers.RotatingFileHandler(filename=logfile,
#                                                     maxBytes=10e6,
#                                                     backupCount=10)
# file_handler.setLevel(logging.INFO)
# file_handler.setFormatter(formatter)
