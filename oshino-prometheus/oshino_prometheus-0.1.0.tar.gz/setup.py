#!/usr/bin/python
# -*- coding: UTF-8 -*-
from setuptools import setup
from pip.req import parse_requirements
from pip.exceptions import InstallationError

from oshino_prometheus.version import get_version

try:
    install_reqs = list(parse_requirements("requirements.txt", session={}))
except InstallationError:
    # There are no requirements
    install_reqs = []

setup(name="oshino_prometheus",
      version=get_version(),
      description="Read metrics from Prometheus",
      author="Šarūnas Navickas",
      author_email="zaibacu@gmail.com",
      packages=["oshino_prometheus"],
      install_requires=[str(ir.req) for ir in install_reqs],
      test_suite="pytest",
      tests_require=["pytest", "pytest-cov", "pytest-asyncio", "prometheus_client"],
      setup_requires=["pytest-runner"]
      )
