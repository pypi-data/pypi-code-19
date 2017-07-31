#!/usr/bin/env python
# coding: utf-8

# Copyright (C) 2017 avideo authors (see AUTHORS)

#
#    This file is part of avideo.
#
#    avideo is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    avideo is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with avideo.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function

import os.path
import warnings
import sys

try:
    from setuptools import setup, Command
    setuptools_available = True
except ImportError:
    from distutils.core import setup, Command
    setuptools_available = False
from distutils.spawn import spawn

# Get the version from avideo/version.py without importing the package
exec(compile(open('avideo/version.py').read(),
             'avideo/version.py', 'exec'))

DESCRIPTION = 'YouTube video downloader'
LONG_DESCRIPTION = 'Command-line program to download videos from YouTube.com and other video sites'

if False:
	None
else:
    files_spec = [
        ('etc/bash_completion.d', ['avideo.bash-completion']),
        ('etc/fish/completions', ['avideo.fish']),
        ('share/doc/avideo', ['README.txt']),
        ('share/man/man1', ['avideo.1'])
    ]
    root = os.path.dirname(os.path.abspath(__file__))
    data_files = []
    for dirname, files in files_spec:
        resfiles = []
        for fn in files:
            if not os.path.exists(fn):
                warnings.warn('Skipping file %s since it is not present. Type  make  to build all automatically generated files.' % fn)
            else:
                resfiles.append(fn)
        data_files.append((dirname, resfiles))

    params = {
        'data_files': data_files,
    }
    if setuptools_available:
        params['entry_points'] = {'console_scripts': ['avideo = avideo:main']}
    else:
        params['scripts'] = ['bin/avideo']

class build_lazy_extractors(Command):
    description = 'Build the extractor lazy loading module'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        spawn(
            [sys.executable, 'devscripts/make_lazy_extractors.py', 'avideo/extractor/lazy_extractors.py'],
            dry_run=self.dry_run,
        )

setup(
    name='avideo',
    version=__version__,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url='https://notabug.org/GPast/avideo',
    author='Grace P.',
    author_email='gpast_panama@protonmail.com',
    maintainer='Grace P.',
    maintainer_email='gpast_panama@protonmail.com',
    packages=[
        'avideo',
        'avideo.extractor', 'avideo.downloader',
        'avideo.postprocessor'],

    # Provokes warning on most systems (why?!)
    # test_suite = 'nose.collector',
    # test_requires = ['nosetest'],

    classifiers=[
        'Topic :: Multimedia :: Video',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],

    cmdclass={'build_lazy_extractors': build_lazy_extractors},
    **params
)
