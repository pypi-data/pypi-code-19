#!/usr/bin/python
# -*- coding: UTF-8 -*-
from setuptools import setup
from pip.req import parse_requirements
from pip.exceptions import InstallationError

from oshino_hw.version import get_version

try:
    install_reqs = list(parse_requirements("requirements.txt", session={}))
except InstallationError:
    # There are no requirements
    install_reqs = []

setup(name="oshino-hw",
      version=get_version(),
      description="An agent to retrieve HW info",
      author="Šarūnas Navickas",
      packages=["oshino_hw"],
      install_requires=[str(ir.req) for ir in install_reqs],
      test_suite="pytest",
      tests_require=["pytest", "pytest-cov", "pytest-asyncio"],
      setup_requires=["pytest-runner"]
      )
