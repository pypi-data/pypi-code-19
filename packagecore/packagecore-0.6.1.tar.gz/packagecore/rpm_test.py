##
# @file rpm_test.py
# @brief Unit tests for the RPM class.
# @author Dominique LaSalle <dominique@bytepackager.com>
# Copyright 2017, Solid Lake LLC
# @version 1
# @date 2017-05-28



import unittest

from .builddata import generateMockData
from .docker import MockContainer
from .rpm import RPM



class TestRPM(unittest.TestCase):
  def test_generateSpecFile(self):
    d = generateMockData() 
    c = MockContainer()
    b = RPM(d, "%s-%s-%d.rpm")

    b.prep(c)

    with open(b._specFile, "r") as ctrlFile:
      content = ctrlFile.read()

    # perform a simplified check on the control file
    self.assertGreaterEqual(content.find("Name: %s" % d.name), 0)


  def test_getName(self):
    d = generateMockData() 
    c = MockContainer()
    b = RPM(d, "%s-%s-%d.rpm")

    name = b.getName()

    self.assertGreaterEqual(name.find(d.name),0)
    self.assertGreaterEqual(name.find(d.version),0)


if __name__ == '__main__':
  unittest.main()
