# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Sqreen python agent package
"""
from .vendors import install_vendors
install_vendors()  # noqa

from .config import Config
from .log import configure_root_logger
from .runner_thread import start
from .sdk.auth import auth_track, signup_track

__author__ = 'Boris Feld'
__email__ = 'boris@sqreen.io'
__version__ = '1.4.0'
VERSION = __version__

# Configure logging
config = Config()
config.load()
configure_root_logger(config['LOG_LEVEL'], config['LOG_LOCATION'])

__all__ = [
    '__author',
    '__email__',
    '__version__',
    'start',
    'auth_track',
    'signup_track',
]
