#!/usr/bin/env python3
# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4 -*-
#
# Copyright (C) 2015-2017 Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import codecs
import os
import re
import sys

from setuptools import setup

version = '2.33'
# look/set what version we have
changelog = 'debian/changelog'
if os.path.exists(changelog):
    head = codecs.open(changelog, encoding='utf-8').readline()
    match = re.compile('.*\((.*)\).*').match(head)
    if match:
        version = match.group(1)


packages = [
    'click',
    'configparser',
    'file-magic',
    'jsonschema',
    'libarchive-c',
    'progressbar33',
    'PyYAML',
    'pyxdg',
    'requests',
    'requests-toolbelt',
    'responses',
    'petname',
    'pymacaroons',
    'pymacaroons-pynacl',
    'simplejson',
    'tabulate',
    'python-debian',
    'chardet',
]

if sys.platform == 'linux':
    packages.extend(['python-distutils-extra', 'python-apt'])

if sys.version < '3.6':
    packages.append('pysha3')


setup(
    name='snapcraft',
    author='Sergio Schvezov <sergio.schvezov@canonical.com>',
    version=version,
    description='Easily craft snaps from multiple sources',
    author_email='snapcraft@lists.snapcraft.io',
    url='https://github.com/snapcore/snapcraft',
    packages=['snapcraft',
              'snapcraft.cli',
              'snapcraft.integrations',
              'snapcraft.internal',
              'snapcraft.internal.cache',
              'snapcraft.internal.deltas',
              'snapcraft.internal.pluginhandler',
              'snapcraft.internal.pluginhandler.stage_package_grammar',
              'snapcraft.internal.repo',
              'snapcraft.internal.sources',
              'snapcraft.internal.states',
              'snapcraft.plugins',
              'snapcraft.storeapi'],
    package_data={'snapcraft.internal.repo': ['manifest.txt']},
    entry_points={
        'console_scripts': [
            'snapcraft = snapcraft.cli.__main__:run',
            'snapcraft-parser = snapcraft.internal.parser:main',
        ],
    },
    data_files=[
        ('share/snapcraft/schema',
            ['schema/' + x for x in os.listdir('schema')]),
        ('share/snapcraft/libraries',
            ['libraries/' + x for x in os.listdir('libraries')]),
    ],
    dependency_links=[
        'https://launchpad.net/python-distutils-extra/trunk/2.39/+download/python-distutils-extra-2.39.tar.gz#egg=python-distutils-extra-2.39',
        'https://launchpad.net/ubuntu/+archive/primary/+files/python-apt_1.1.0~beta1build1.tar.xz#egg=python-apt-1.1.0~betabuild1',
    ],
    install_requires=packages,
    test_suite='snapcraft.tests',
    license='GPL v3',
    classifiers=(
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Build Tools',
        'Topic :: System :: Software Distribution',
    ),
)
