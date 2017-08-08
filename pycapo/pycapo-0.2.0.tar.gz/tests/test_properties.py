# -*- coding: utf-8 -*-

import os

import pytest
from pycapo import CapoConfig

OPTIONS = (
    {
        'int.test': 12,
        'float.test': 123.456,
        'string.test': 'foo',
        'misc.test': 'mook',
        'bool.test': 'false',
        'env.test': '${env:FOO}/tmp'
    },
    {
        'int.test': 21,
        'float.test': 654.321,
        'string.test': 'bar',
        'other.test': 'b test',
        'bool.test': 'true',
    }
)


class CapoTest:
    """ A class that builds a test environment for pycapo with two
    properties files, a/test.properties and b/test.properties, with
    options defined in the OPTOINS dict above. """

    def __init__(self, tmpdir):
        self.tmpdir = tmpdir
        self.dirs = (tmpdir.mkdir('a'), tmpdir.mkdir('b'))
        self.path = ':'.join([os.path.join(ld.dirname, ld.basename)
                              for ld in self.dirs])
        self.profile = 'test'
        self.write_files()

    def write_files(self):
        for opts, directory in zip(OPTIONS, self.dirs):
            self._write_file(opts, directory)

    def _write_file(self, opts, directory):
        f = directory.join(self.profile + '.properties')
        f.write('# test comment with a pound sign\n', mode='w')
        f.write('; test comment with a semi-colon\n', mode='a')
        f.write('\n\t\n', mode='a')
        for key in opts:
            f.write("{}={}\n".format(key, opts[key]), mode='a')

    def nuke_file(self, n):
        self.dirs[n].remove(rec=1)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tmpdir.remove()


@pytest.fixture
def capotest(tmpdir):
    return CapoTest(tmpdir)


# Tests for checking 'get' operations with a hierarchy of files, these
# tests check simple property fetching, but also how a property defined
# in a later file can over-ride the same property from an earlier file.

def test_static_float(capotest):
    """ A float test, float.test should be 654.321 """
    c = CapoConfig(path=capotest.path, profile=capotest.profile)
    assert c.getfloat('float.test') == 654.321


def test_static_int(capotest):
    """ An int test, int.test should be 21"""
    c = CapoConfig(path=capotest.path, profile=capotest.profile)
    assert c.getint('int.test') == 21


def test_static_bool(capotest):
    """ A bool test, bool.test should be True """
    c = CapoConfig(path=capotest.path, profile=capotest.profile)
    assert c.getboolean('bool.test')


def test_static_string(capotest):
    c = CapoConfig(path=capotest.path, profile=capotest.profile)
    assert c.getstring('string.test') == 'bar'


def test_env_expansion(capotest, monkeypatch):
    """ Test environment variable expansion """
    monkeypatch.setenv('FOO', 'foo')
    c = CapoConfig(path=capotest.path, profile=capotest.profile)
    assert c.getstring('env.test') == 'foo/tmp'


# Slightly more devious: read a property from the full environment, then
# delete the second file and read the property again, the two values should
# be different, in the absence of the second file pycapo should re-read
# them all, resulting in the first file's value being returned.

def test_caching_float(capotest):
    c = CapoConfig(path=capotest.path, profile=capotest.profile)
    capotest.write_files()
    a = c.getfloat('float.test')
    capotest.nuke_file(1)
    b = c.getfloat('float.test')
    assert a != b and b == 123.456


def test_caching_int(capotest):
    c = CapoConfig(path=capotest.path, profile=capotest.profile)
    capotest.write_files()
    a = c.getint('int.test')
    capotest.nuke_file(1)
    b = c.getint('int.test')
    assert a != b and b == 12


def test_caching_bool(capotest):
    c = CapoConfig(path=capotest.path, profile=capotest.profile)
    capotest.write_files()
    a = c.getboolean('bool.test')
    capotest.nuke_file(1)
    b = c.getboolean('bool.test')
    assert a != b and not b


def test_caching_string(capotest):
    c = CapoConfig(path=capotest.path, profile=capotest.profile)
    capotest.write_files()
    a = c.getstring('string.test')
    capotest.nuke_file(1)
    b = c.getstring('string.test')
    assert a != b and b == 'foo'
