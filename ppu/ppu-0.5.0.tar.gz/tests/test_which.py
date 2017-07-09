#! /usr/bin/env python

import os
import subprocess
import sys
from ppu_tu import setup, teardown, find_in_path  # noqa


tmp_dir = None

test_prog_path = find_in_path('which.py')
if not test_prog_path:
    sys.exit("Cannot find which.py in %s" % os.environ["PATH"])


def test_which():
    assert subprocess.check_output(
        [sys.executable, test_prog_path, "which.py"],
        universal_newlines=True).strip() == test_prog_path
    assert subprocess.check_output(
        [sys.executable, test_prog_path, "WhoWhereWhenceWhichWhereIs.py"],
        universal_newlines=True).strip() == ''
