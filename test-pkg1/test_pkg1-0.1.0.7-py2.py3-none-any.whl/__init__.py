# -*- coding: utf-8 -*-

"""Top-level package for test_pkg1."""

__author__ = """Shmuel Maruani"""
__email__ = 'shmuel@limitlessv.com'
__version__ = '0.0.1'

from ._version_old import get_versions
__version__ = get_versions()['version']
del get_versions
