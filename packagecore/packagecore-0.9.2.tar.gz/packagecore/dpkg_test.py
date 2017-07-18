##
# @file chroot_test.py
# @brief Unit tests for the DebianPackage class.
# @author Dominique LaSalle <dominique@bytepackager.com>
# Copyright 2017, Solid Lake LLC
# @version 1
# @date 2017-05-27


import unittest
import os

from .builddata import generateMockData
from .docker import MockContainer
from .dpkg import DebianPackage





class TestDpkg(unittest.TestCase):
  def test_generateControlFile(self):
    d = generateMockData() 
    c = MockContainer()
    b = DebianPackage(d)

    b.prep(c)

    with open(os.path.join(c.getSharedDir(), "%s-%s/DEBIAN/control" % \
        (d.name, d.version)), "r") as ctrlFile:
      content = ctrlFile.read()

    # perform a simplified check on the control file
    self.assertGreaterEqual(content.find("Package: %s" % d.name), 0)


  def test_generateCopyrightFile(self):
    d = generateMockData() 
    c = MockContainer()
    b = DebianPackage(d)

    b.prep(c)

    with open(os.path.join(c.getSharedDir(), "%s-%s/DEBIAN/copyright" % \
        (d.name, d.version)), "r") as ctrlFile:
      content = ctrlFile.read()

    # perform a simplified check on the control file
    self.assertGreaterEqual(content.find("License: %s" % d.license), 0) 


  def test_postInstallFile(self):
    d = generateMockData() 
    c = MockContainer()
    b = DebianPackage(d)

    b.prep(c)

    with open(os.path.join(c.getSharedDir(), "%s-%s/DEBIAN/postinst" % \
        (d.name, d.version)), "r") as ctrlFile:
      content = ctrlFile.read()

    # perform a simplified check on the control file
    self.assertEqual(content.find("#!/bin/bash"), 0)
    self.assertGreaterEqual(content.find("adduser"), 0)


  def test_getName(self):
    d = generateMockData() 
    c = MockContainer()
    b = DebianPackage(d)

    name = b.getName()

    self.assertGreaterEqual(name.find(d.name),0)
    self.assertGreaterEqual(name.find(d.version),0)


if __name__ == '__main__':
  unittest.main()
