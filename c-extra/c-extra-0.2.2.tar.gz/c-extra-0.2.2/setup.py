#!/usr/bin/env python3

from distutils.core import setup

name     = "c-extra"
base_url = "http://chadok.info/c-extra"
version  = "0.2.2"

try:
    with open('README.rst') as file:
        long_description = file.read()
except:
    long_description = ""

setup(
    name         = name,
    version      = version,
    description  = "Non official client for Crypto-Extranet",
    long_description = long_description,
    author       = "Olivier Schwander",
    author_email = "olivier.schwander@chadok.info",
    url          = base_url,
    download_url = base_url + "/" + name + "-" + version + ".tar.gz",
    packages     = [],
    scripts      = ["c-extra"],
    requires     = ["requests", "tabulate"],
    classifiers  = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        ],
)

