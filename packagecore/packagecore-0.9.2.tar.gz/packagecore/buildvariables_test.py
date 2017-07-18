##
# @file buildvariables_test.py
# @brief Unit tests for the buildvariables object.
# @author Dominique LaSalle <dominique@bytepackager.com>
# Copyright 2017, Solid Lake LLC
# @version 1
# @date 2017-07-03



import unittest
from .buildvariables import * 


TEST_DESTDIR="/tmp/fakeroot"
TEST_SOURCEDIR="/tmp/my-pkg/src"


class MockFile(object):
  def __init__(self):
    self._buffer = []

  def write(self, chunk):
    self._buffer.append(chunk)

  def getBuffer(self):
    return ''.join(self._buffer)


class TestBuildVariables(unittest.TestCase):
  def test_write(self):
    b = BuildVariables(destDir=TEST_DESTDIR, sourceDir=TEST_SOURCEDIR)
  
    m = MockFile()
    b.write(m)

    output = m.getBuffer()
    self.assertTrue(("%s=\"%s\"\n" % (DESTDIR_KEY, TEST_DESTDIR)) in output)
    self.assertTrue( \
        ("%s=\"%s\"\n" % (SOURCEDIR_KEY, TEST_SOURCEDIR)) in output)


  def test_generate(self):
    b = BuildVariables(destDir=TEST_DESTDIR, sourceDir=TEST_SOURCEDIR)
  
    d  = b.generate()

    self.assertEqual(d[DESTDIR_KEY], TEST_DESTDIR)
    self.assertEqual(d[SOURCEDIR_KEY], TEST_SOURCEDIR)


if __name__ == '__main__':
  unittest.main()
