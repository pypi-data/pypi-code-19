"""PPU test utilities"""


import os
import shutil
from tempfile import mkdtemp


def setup():
    global tmp_dir
    tmp_dir = mkdtemp()
    os.chdir(tmp_dir)


def teardown():
    os.chdir(os.sep)  # To the root of the FS
    shutil.rmtree(tmp_dir)


def find_in_path(name):
    for path in os.environ["PATH"].split(os.pathsep):
        path = path.strip('"')
        test_prog_path = os.path.join(path, name)
        if os.path.exists(test_prog_path):
            return test_prog_path


def create_files(files, subdirectory=None):
    if subdirectory:
        os.makedirs(subdirectory)
    else:
        subdirectory = ''
    for fname in files:
        with open(os.path.join(subdirectory, fname), 'w'):
            pass


def assert_files_exist(files):
    if isinstance(files, str):
        files = [files]
    for fname in files:
        assert os.path.exists(fname)


def assert_files_not_exist(files):
    if isinstance(files, str):
        files = [files]
    for fname in files:
        assert not os.path.exists(fname)
