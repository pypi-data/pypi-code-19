import os
import sys
import json

# CHECK DEPENDENCIES

# check python version
if sys.version_info < (2, 7):
    raise RuntimeError("Fatal error: Python 2.7+ is required for this package.")

# RETRIEVE PACKAGE INFORMATION FROM CONFIG FILE

try:
    import __conf__
    config = __conf__.config_map
except ImportError:
    raise RuntimeError("Fatal error: Configuration module is missing.")

__author__ = config["author"]
__version__ = config["version"]
__version_info__ = tuple([int(d) for d in __version__.split(".")])
