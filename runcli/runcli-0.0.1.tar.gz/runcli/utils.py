"""
runcli.utils
============
Utilities for the ``runcli`` package.
"""

import logging
import tempfile
import shutil


logger = logging.getLogger(__name__)


# eventually this context manager should be replaced with
# tempfile.TemporaryDirectory when only newer versions of python are
# targeted by this project.
class TemporaryDirectory(object):
    """A context manager that creates a temporary directory.

    This context manager returns the path to a temporary directory which
    is destroyed upon exiting the context.

    Use this context manager for python 2.7 compatibility. A version of
    this context manager exists in the tempfile module in newer versions
    of python.
    """

    def __enter__(self):
        """Create an return a temporary directory."""
        self.tmp_dir_path = tempfile.mkdtemp()
        return self.tmp_dir_path

    def __exit__(self, *args):
        """Remove the temporary directory created by __enter__."""
        shutil.rmtree(self.tmp_dir_path)
