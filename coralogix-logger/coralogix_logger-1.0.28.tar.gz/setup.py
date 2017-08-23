##!/usr/bin/env python

import os

try:
    from setuptools import setup, find_packages
except:
    import ez_setup
    ez_setup.use_setuptools()

#Package name
_PKG_NAME = "coralogix_logger"

#Version
try:
    VERSION_FILE = os.path.join(os.path.abspath(os.path.curdir), "coralogix/VERSION")
    with open(VERSION_FILE, mode="r") as version_file:
        _PKG_VERSION = version_file.read().strip()
except Exception:
    _PKG_VERSION = '0.0.0'

#Description file
try:
    README_FILE = os.path.join(os.path.abspath(os.path.curdir), "README.txt")
    with open(README_FILE, mode="r") as input_file:
        _PKG_DESCRIPTION = input_file.read()
except Exception:
    _PKG_DESCRIPTION = 'No Description'

setup(
    include_package_data = True,
    name =              _PKG_NAME,
    version =           _PKG_VERSION,
    license =           "MIT",
    description =       "Coralogix Logger Python SDK",
    long_description =  _PKG_DESCRIPTION,
    author =            "Coralogix Ltd.",
    author_email =      "royee@coralogix.com",
    url =               "http://www.coralogix.com/",
    packages =          find_packages(exclude=[".vscode", "teste*.py", "tester", "*.pyc", "*.log", ".gitignore"]),
    install_requires =  ["enum34", "httplib2"],
    package_data =      {},
    dependency_links =  [],
    scripts =           [],
    entry_points =      {},
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License"]
)