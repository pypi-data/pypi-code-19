# -*- coding: utf-8 -*-

"""
Discoin API Wrapper
~~~~~~~~~~~~~~~~~~~
An API wrapper for the Discoin API.

"""

__title__ = 'discoin'
__author__ = 'Joseph Banks'
__license__ = 'MIT'
__copyright__ = 'Copyright 2017-Present Joseph Banks'
__version__ = '1.0.1'

from .errors import DiscoinError
from .classes import Transaction
from .client import Discoin
