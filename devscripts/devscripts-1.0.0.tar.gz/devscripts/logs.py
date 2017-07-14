#!/usr/bin/env python
"""
Simple logging module made for development
"""
import logging

FORMAT = '%(asctime)s :: %(levelname)s :: %(message)s'


def simple_logger(**kwargs):
    '''
    Creates a simple logger

    :param str name: The logger's name ('api', 'back'...)
    :param int base_level: Lowest level allowed to log (Default: DEBUG)
    :param str log_format: Logging format used for STDOUT
                           (Default: logs.FORMAT)

    :param bool should_stdout: Allows to log to stdout (Default: True)
    :param int stdout_level: Lowest level allowed to log to STDOUT
                             (Default: DEBUG)

    :param bool should_http: Allows to log to HTTP server
    :param int http_level: Lowest level allowed to log to the HTTP server
                           (Has to be superior or equals to base_level)
    :param str http_host: Address of the HTTP Server
    :param str http_url: Url of the HTTP Server
    '''
    # Args
    logger_name = kwargs.get('name')
    base_level = kwargs.get('base_level', logging.DEBUG)

    should_stdout = kwargs.get('should_stdout', True)

    should_http = kwargs.get('should_http', False)

    # Generate base logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(base_level)

    # Define stdout handler
    if should_stdout:
        logger.addHandler(_add_stream_handler(**kwargs))

    if should_http:
        logger.addHandler(_add_http_handler(**kwargs))
    return logger


def _add_stream_handler(**kwargs):
    stdout_level = kwargs.get('stdout_level', logging.DEBUG)
    log_format = kwargs.get('log_format', FORMAT)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(log_format)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(stdout_level)
    return stream_handler


def _add_http_handler(**kwargs):
    http_level = kwargs.get('http_level', logging.INFO)
    http_host = kwargs.get('http_host')
    http_url = kwargs.get('http_url')
    http_method = kwargs.get('http_method', 'GET')
    http_credentials = kwargs.get('http_credentials')
    http_context = kwargs.get('http_context')
    http_secure = kwargs.get('secure', False)

    http_handler = logging.handlers.HTTPHandler(
        host=http_host,
        url=http_url,
        secure=http_secure,
        method=http_method,
        credentials=http_credentials,
        context=http_context
    )

    http_handler.setLevel(http_level)
    return http_handler
