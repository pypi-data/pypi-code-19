# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Logging module helpers
"""
import logging

ROOT_LOGGER_NAME = 'sqreen'
LOG_FORMAT = ('[%(levelname)s][%(asctime)s #%(process)d.%(threadName)s]'
              ' %(name)s:%(lineno)s \t%(message)s')


def configure_root_logger(log_level, log_location=None):
    """ Configure the sqreen root logger. Set following settings:

    - log_level

    Ensure that the sqreen root logger don't propagate messages logs
    to the python root logger.
    Configure two handlers, one stream handler on stderr for errors
    and one file handler if log_location is set for configured level
    """
    logger = logging.getLogger(ROOT_LOGGER_NAME)

    # Don't propagate messages to upper loggers
    logger.propagate = False

    formatter = logging.Formatter(LOG_FORMAT)

    # Only add handler once
    if len(logger.handlers) is 0:

        # Configure the stderr handler configured on CRITICAL level
        stderr_handler = logging.StreamHandler()
        stderr_handler.setFormatter(formatter)
        logger.addHandler(stderr_handler)

        if log_location is not None:
            try:
                handler = logging.FileHandler(log_location)

                handler.setFormatter(formatter)
                logger.addHandler(handler)
            except (OSError, IOError):
                msg = "Couldn't use %s as sqreen log location, fallback to stderr."
                logger.exception(msg, log_location)

    try:
        logger.setLevel(log_level)
    except ValueError:
        logger.error("Unknown log_level %r, don't alter log level", log_level)

    return logger
