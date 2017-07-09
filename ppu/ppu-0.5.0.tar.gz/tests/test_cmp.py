#! /usr/bin/env python

import os
import subprocess
import sys
from ppu_tu import setup, teardown, find_in_path  # noqa


tmp_dir = None

test_prog_path = find_in_path('cmp.py')
if not test_prog_path:
    sys.exit("Cannot find cmp.py in %s" % os.environ["PATH"])


def create_file(name, content):
    with open(name, 'w') as fp:
        fp.write(content)


def test_cmp_equal():
    create_file('test1', 'test')
    create_file('test2', 'test')
    assert subprocess.call(
        [sys.executable, test_prog_path, "-i", "test1", "test2"]) == 0

    create_file('test3', 'test3')
    create_file('test4', 'test4')
    assert subprocess.call(
        [sys.executable, test_prog_path, "-i", "test3", "test4"]) == 1
