"""
test_endtoend
=============
An end to end test for runcli.
"""

import logging
import os
import stat
import subprocess
import tempfile
import unittest

from runcli import utils


logger = logging.getLogger(__name__)


class EndToEndTest(unittest.TestCase):
    """Test runcli project end-to-end."""

    def test_end_to_end(self):
        """Test runcli project end-to-end."""
        with utils.TemporaryDirectory() as tmp_dir_path:
            runfile_path = os.path.join(tmp_dir_path, 'Runfile')
            with open(runfile_path, 'w') as runfile:
                runfile.write(
                    '#! /bin/bash\n'
                    'echo $@\n')
            # make the runfile executable
            os.chmod(
                runfile_path,
                os.stat(runfile_path).st_mode | stat.S_IEXEC)

            # perform an end-to-end test in the same directory as the
            # Runfile
            os.chdir(tmp_dir_path)
            self.assertEqual(
                subprocess.check_output(
                    'run this is a test',
                    shell=True).decode('utf-8'),
                'this is a test\n')

            # perform an end-to-end test in a subdirectory of the
            # directory containing the Runfile
            subdir_path = os.path.join(tmp_dir_path, 'foo')
            os.mkdir(subdir_path)
            os.chdir(subdir_path)
            self.assertEqual(
                subprocess.check_output(
                    'run this is another test',
                    shell=True).decode('utf-8'),
                'this is another test\n')

            # perform an end-to-end test in a sub-sub directory of the
            # directory containing the Runfile
            subsubdir_path = os.path.join(subdir_path, 'bar')
            os.mkdir(subsubdir_path)
            os.chdir(subsubdir_path)
            self.assertEqual(
                subprocess.check_output(
                    'run this is another another test',
                    shell=True).decode('utf-8'),
                'this is another another test\n')
