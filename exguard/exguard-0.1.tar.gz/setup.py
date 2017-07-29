#!/usr/bin/env python3

# exguard - Guard code against exceptions, e.g. for running untrusted module code in a framework
# This file is not copyrightable.

import os
from setuptools import setup

setup(
    name='exguard',
    version='0.1',
    summary='Guard code against exceptions, e.g. for running untrusted module code in a framework',
    long_description = open(os.path.join(os.path.dirname(__file__), "README.rst"),
                            "r", encoding="utf-8").read(),
    url="https://edugit.org/Veripeditus/exguard",
    author="Eike Tim Jesinghaus",
    author_email="eike@naturalnet.de",
    py_modules=['exguard'],
    zip_safe=False,
    python_requires=">=3.5",
    classifiers=[
                 "Development Status :: 4 - Beta",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
                 "Programming Language :: Python :: 3",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                ],
)
