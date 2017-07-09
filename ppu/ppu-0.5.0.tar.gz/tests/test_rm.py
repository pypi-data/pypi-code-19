#! /usr/bin/env python

import os
import subprocess
import sys
from ppu_tu import setup, teardown, find_in_path  # noqa
from ppu_tu import create_files, assert_files_exist, assert_files_not_exist


tmp_dir = None

test_prog_path = find_in_path('rm.py')
if not test_prog_path:
    sys.exit("Cannot find rm.py in %s" % os.environ["PATH"])


def test_rm():
    create_files(['test1', 'test2'])
    assert_files_exist(['test1', 'test2'])
    assert subprocess.call(
        [sys.executable, test_prog_path, "test2"]) == 0
    assert_files_exist('test1')
    assert_files_not_exist('test2')

    create_files(['test1', 'test2'])
    assert_files_exist(['test1', 'test2'])
    assert subprocess.call(
        [sys.executable, test_prog_path, "-r", "test2"]) == 0
    assert_files_exist('test1')
    assert_files_not_exist('test2')


def test_rm_recursive():
    create_files(['test'])
    create_files(['test'], 'subdir/subd2')
    assert_files_exist(['test', 'subdir/subd2/test'])
    assert subprocess.call(
        [sys.executable, test_prog_path, "subdir"]) == 1
    assert subprocess.call(
        [sys.executable, test_prog_path, "-r", "subdir"]) == 0
    assert_files_exist('test')
    assert_files_not_exist(['subdir/subd2/test'])
