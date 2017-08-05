# coding: utf-8

"""
A Python client for the Public Transport of Victoria's application programming
interface.
"""

import os
import re
import sys

from setuptools import setup

major, minor1, minor2, release, serial =  sys.version_info

readfile_kwargs = {"encoding": "utf-8"} if major >= 3 else {}

def readfile(filename):
    with open(filename, **readfile_kwargs) as fp:
        contents = fp.read()
    return contents

version_regex = re.compile("__version__ = \"(.*?)\"")
contents = readfile(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "ptv", "__init__.py"))

version = version_regex.findall(contents)[0]

setup(name="ptv",
      version=version,
      author="Andrew R. Casey",
      author_email="andycasey@gmail.com",
      packages=["ptv"],
      url="http://www.github.com/andycasey/ptv/",
      license="MIT",
      description="Python client for the Public Transport Victoria real-time API",
      long_description=\
          readfile(os.path.join(os.path.dirname(__file__), "README.md"))
     )