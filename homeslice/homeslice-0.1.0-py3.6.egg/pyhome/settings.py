"""
Some simple settings for use in other parts of the tool.
"""

from __future__ import absolute_import, print_function

import os

HOME = os.environ['HOME']
HOMESLICE_ROOT = os.path.join(HOME, '.config/homeslice')
HOMESLICE_REPO = os.path.join(HOMESLICE_ROOT, 'repos')
