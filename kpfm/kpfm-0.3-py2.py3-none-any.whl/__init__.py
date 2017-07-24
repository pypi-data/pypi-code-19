# -*- coding: utf-8 -*-
"""
============================
kpfm
============================
"""

# Versioneer versioning
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from kpfm.util import h5ls