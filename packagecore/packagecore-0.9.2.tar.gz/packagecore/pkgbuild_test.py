##
# @file pkgbuild_test.py
# @brief Unit tests for the pkgbuild class.
# @author Dominique LaSalle <dominique@bytepackager.com>
# Copyright 2017, Solid Lake LLC
# @version 1
# @date 2017-05-28



import unittest
import os

from .builddata import generateMockData
from .docker import MockContainer
from .pkgbuild import PkgBuild 






class TestPkgBuild(unittest.TestCase):
  def test_generatePKGBUILDFile(self):
    d = generateMockData() 
    c = MockContainer()
    b = PkgBuild(d)

    b.prep(c)

    with open(os.path.join(c.getSharedDir(), "arch-pkg/PKGBUILD")) as ctrlFile:
      content = ctrlFile.read()

    # perform a simplified check on the control file
    self.assertGreaterEqual(content.find("pkgname=%s" % d.name), 0)


  def test_getName(self):
    d = generateMockData() 
    c = MockContainer()
    b = PkgBuild(d)

    name = b.getName()

    self.assertGreaterEqual(name.find(d.name),0)
    self.assertGreaterEqual(name.find(d.version),0)


if __name__ == '__main__':
  unittest.main()
