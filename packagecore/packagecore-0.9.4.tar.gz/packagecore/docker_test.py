##
# @file docker_test.py
# @brief Unit tests for docker.py
# @author Dominique LaSalle <dominique@solidlake.com>
# Copyright 2017, Solid Lake LLC
# @version 1
# @date 2017-08-08



import unittest

from .docker import * 
from .distributions import *


class TestDocker(unittest.TestCase):
  def test_runCommand(self):
    # attempt to download and run a simple ls on a container
    d = Docker()

    # centos is nice and stable
    c = d.start(DATA["centos7.3"]["dockerImage"])

    # should succeed
    c.execute("ls")

    # should fail
    try:
      cmd = ["ls", "/dev/null/nothing"]
      c.execute(cmd)

      # should have failed
      self.Fail("'%s' did not throw an exception." % str(cmd))
    except DockerError as e:
      # success
      pass
      
    d.stop(c)
