#! /usr/bin/env python

from time import time
import os
import subprocess
import sys
from ppu_tu import setup, teardown, find_in_path  # noqa
from ppu_tu import create_files, assert_files_exist, assert_files_not_exist


tmp_dir = None
old_time = time() - 1000 * 24 * 3600  # 1000 days ago

test_prog_path = find_in_path('remove-old-files.py')
if not test_prog_path:
    sys.exit("Cannot find remove-old-files.py in %s" % os.environ["PATH"])


def test_remove_old_files():
    create_files(['test1', 'test2'])
    assert_files_exist(['test1', 'test2'])
    os.utime('test2', (old_time, old_time))
    assert subprocess.call(
        [sys.executable, test_prog_path, "--older", "100", "."]) == 0
    assert_files_exist('test1')
    assert_files_not_exist('test2')


def test_recursive():
    create_files(['test3', 'test4'], 'subdir')
    test3 = os.path.join('subdir', 'test3')
    test4 = os.path.join('subdir', 'test4')
    assert_files_exist([test3, test4])
    os.utime(test4, (old_time, old_time))
    assert subprocess.call(
        [sys.executable, test_prog_path, "--older", "100", "."]) == 0
    assert_files_exist(test3)
    assert_files_not_exist(test4)


def test_remove_empty_directory():
    create_files(['test3', 'test4'], 'subdir')
    test3 = os.path.join('subdir', 'test3')
    test4 = os.path.join('subdir', 'test4')
    assert_files_exist([test3, test4])
    os.utime(test3, (old_time, old_time))
    os.utime(test4, (old_time, old_time))
    assert subprocess.call(
        [sys.executable, test_prog_path, "--older", "100", "."]) == 0
    assert_files_exist('subdir')
    assert_files_not_exist([test3, test4])
    assert subprocess.call(
        [sys.executable, test_prog_path, "-e", "--older", "100", "."]) == 0
    assert_files_not_exist('subdir')
