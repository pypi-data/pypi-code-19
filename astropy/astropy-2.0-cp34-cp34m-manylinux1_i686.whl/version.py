# Autogenerated by Astropy's setup.py on 2017-07-07 08:47:25.120641
from __future__ import unicode_literals
import datetime

version = "2.0"
githash = ""


major = 2
minor = 0
bugfix = 0

release = True
timestamp = datetime.datetime(2017, 7, 7, 8, 47, 25, 120641)
debug = False

try:
    from ._compiler import compiler
except ImportError:
    compiler = "unknown"

try:
    from .cython_version import cython_version
except ImportError:
    cython_version = "unknown"
