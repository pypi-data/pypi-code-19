
import sys, os, imp
from os.path import dirname, abspath, join


def add_to_path():
    """
    Prepends the build directory to the path so that newly built libraries are used, allowing
    it to be tested without installing it.
    """
    # Put the root directory into the path first so we pick up the Python code from the source
    # directories.  It will also be in the build directory, so make sure build is 2nd!

    root = dirname(dirname(abspath(__file__)))
    sys.path.insert(0, root)

    # Put the build directory into the Python path so we pick up the version we just built.
    #
    # To make this cross platform, we'll search the directories until we find the .pyd file.

    prefix = '_pglib'

    library_exts  = [t[0] for t in imp.get_suffixes() if t[-1] == imp.C_EXTENSION]
    library_names = [prefix + ext for ext in library_exts]

    # Only go into directories that match the current Python's version number.

    dir_suffix = '-%s.%s' % (sys.version_info[0], sys.version_info[1])

    build = join(dirname(dirname(abspath(__file__))), 'build')

    for root, dirs, files in os.walk(build):
        for d in dirs[:]:
            if not d.endswith(dir_suffix):
                dirs.remove(d)

        for name in library_names:
            if name in files:
                sys.path.insert(1, root)
                return

    sys.exit('Did not find the build directory')


_TESTSTR = '0123456789-abcdefghijklmnopqrstuvwxyz-'


def generate_test_string(length):
    """
    Returns a string of composed of `seed` to make a string `length` characters long.

    To enhance performance, there are 3 ways data is read, based on the length of the value, so most data types are
    tested with 3 lengths.  This function helps us generate the test data.

    We use a recognizable data set instead of a single character to make it less likely that "overlap" errors will
    be hidden and to help us manually identify where a break occurs.
    """
    if length <= len(_TESTSTR):
        return _TESTSTR[:length]

    c = (length + len(_TESTSTR)-1) // len(_TESTSTR)
    v = _TESTSTR * c
    return v[:length]
