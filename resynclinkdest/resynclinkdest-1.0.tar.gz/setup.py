#!/usr/bin/env python
# This file is part of resynclinkdest.
#
# resynclinkdest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# resynclinkdest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with resynclinkdest.  If not, see <http://www.gnu.org/licenses/>.
from os.path import join, dirname
import sys
from setuptools import setup
extra = {}
if sys.version_info >= (3, ):
    extra['use_2to3'] = True

setup(
    name='resynclinkdest',
    version='1.0',
    author='Vincent Pelletier',
    author_email='plr.vincent@gmail.com',
    url='http://github.com/vpelletier/resynclinkdest',
    license='GPL 3+',
    platforms=['any'],
    classifiers=[
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: System :: Archiving :: Backup',
    ],
    py_modules=['resynclinkdest'],
    entry_points={
        'console_scripts': [
            'resynclinkdest=resynclinkdest:main',
        ],
    },
    zip_safe=True,
    **extra
)
