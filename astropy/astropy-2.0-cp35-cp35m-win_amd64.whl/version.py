# Autogenerated by Astropy's setup.py on 2017-07-07 12:47:32.175070
from __future__ import unicode_literals
import datetime

version = "2.0"
githash = "35ef7fd46e81e2b787e6b849a0aa011a8805c02b"


major = 2
minor = 0
bugfix = 0

release = True
timestamp = datetime.datetime(2017, 7, 7, 12, 47, 32, 175070)
debug = False

try:
    from ._compiler import compiler
except ImportError:
    compiler = "unknown"

try:
    from .cython_version import cython_version
except ImportError:
    cython_version = "unknown"
