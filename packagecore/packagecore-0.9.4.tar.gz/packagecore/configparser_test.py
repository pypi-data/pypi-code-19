##
# @file packager_test.py
# @brief Unit tests for the Packager class.
# @author Dominique LaSalle <dominique@bytepackager.com>
# Copyright 2017, Solid Lake LLC
# @version 1
# @date 2017-07-16


import unittest


from .configparser import ConfigParser



CONF = {
"name": "packagecore",
"maintainer": "dominique@bytepackager.com",
"license": "GPL2",
"summary": "Utility for generating Linux packages.",
"homepage": "https://github.com/bytepackager/packagecore",
"commands": {
  "precompile": "echo \"Nothing to do\"",
  "compile": "echo \"Nothing to compile.\"",
  "install": "python3 setup.py install --prefix=/usr --root=\"${BP_DESTDIR}\"",
  "postinstall": "echo \"Finished installing.\"",
  "testinstall": "packagecore -h || exit 1"
},
"packages": {
  "archlinux": {
    "builddeps": [
      "python",
      "python-setuptools"
    ],
    "deps": [
      "python",
      "python-yaml",
      "docker"
    ]
  },
  "fedora25": {
    "builddeps": [
      "python3",
      "python3-setuptools"
    ],
    "deps": [
      "python3",
      "python3-PyYAML",
      "docker"
    ],
  },
  "ubuntu17.10": {
    "builddeps": [
      "python3",
      "python3-setuptools"
    ],
    "deps": [
      "python3",
      "python3-yaml",
      "docker"
    ]
  }
}
}

class TestPackager(unittest.TestCase):
  def test_init(self):
    p = ConfigParser()
    builds = p.parse(CONF, "1.2.3", 4)

    for b in builds:
      self.assertEqual(b.name, CONF["name"])
      self.assertEqual(b.maintainer, CONF["maintainer"])
      self.assertEqual(b.license, CONF["license"])
      self.assertEqual(b.summary, CONF["summary"])
      self.assertEqual(b.homepage, CONF["homepage"])

      self.assertEqual(b.preCompileCommands, CONF["commands"]["precompile"])
      self.assertEqual(b.installCommands, CONF["commands"]["install"])
      self.assertEqual(b.postInstallCommands, CONF["commands"]["postinstall"])
      self.assertEqual(b.testInstallCommands, CONF["commands"]["testinstall"])

      # still need to test listed dependencies and overridden commands

