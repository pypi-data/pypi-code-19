#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2017 Rémi Duraffort
# This file is part of lavacli.
#
# lavacli is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# lavacli is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with lavacli.  If not, see <http://www.gnu.org/licenses/>

from setuptools import setup

from lavacli import __version__

setup(
    name='lavacli',
    version=__version__,
    description='LAVA XML-RPC command line interface',
    author='Rémi Duraffort',
    author_email='ivoire@videolan.org',
    license="AGPLv3+",
    url='https://framagit.org/ivoire/lavacli',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Communications",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Networking",
    ],
    packages=['lavacli', 'lavacli.commands'],
    entry_points={
        'console_scripts': [
            'lavacli = lavacli:main'
        ]
    },
    install_requires=[
        "PyYAML",
        "pyzmq",
        "requests",
  ]
)
