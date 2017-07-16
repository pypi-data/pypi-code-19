# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

import re
from setuptools import setup

import sys
if not sys.version_info[0] == 3:
#    sys.exit("\n \
    print("\n \
              ****************************************************************\n \
              * The CLI has only been tested with Python 3+ at this time.    *\n \
              * Report any issues with Python 2 by emailing help@qio.io *\n \
              ****************************************************************\n")

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('fsight/pio.py').read(),
    re.M
    ).group(1)

setup(
    name = "fsight-cli",
    packages = ["fsight"],
    entry_points = {
        "console_scripts": ['fsight = fsight.pio:main']
    },
    version = version,
    description = "Foresight engine CLI",
    long_description = "Foresight engine CLI",
    author = "Fouad Omri",
    author_email = "fouad.omri@qio.io",
    url = "https://qio.io",
    install_requires=[
        "kubernetes==2.0.0",
        "fire==0.1.0",
        "requests==2.13.0",
        "pyyaml==3.12",
        "dill==0.2.5",
        "tabulate==0.7.7",
        "futures==3.1.1",
        "cloudpickle==0.3.1",
    ],
    dependency_links=[
    ]
)
