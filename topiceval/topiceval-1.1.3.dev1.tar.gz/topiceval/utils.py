"""
This module provides some common utility functions to be shared across modules.
Does not have much as of now.
"""

from __future__ import print_function
from __future__ import division

import os


def verify_filename(filename):
    if not os.path.isfile(filename):
        raise ValueError("Given filepath doesn't exist.")
    return
