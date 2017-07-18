'''
The MIT License (MIT)

Copyright (c) 2014-2017 The OmniDB Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import os
import sys
from setuptools import setup

rootdir = os.path.abspath(os.path.dirname(__file__))
long_description = open(os.path.join(rootdir, 'README.md')).read()

setup(name='OmniDatabase',
      version='0.25',
      description='Generic database metadata and access provider',
      long_description=long_description,
      url='http://github.com/OmniDB/OmniDatabase',
      author='William Ivanski',
      author_email='william.ivanski@gmail.com',
      license='MIT',
      packages=['OmniDatabase'],
      install_requires=['Spartacus'],
      extras_require={
        'postgresql': ['Spartacus[postgresql]'],
        'mysql':      ['Spartacus[mysql]'],
        'mariadb':    ['Spartacus[mariadb]'],
        'firebird':   ['Spartacus[firebird]'],
        'oracle':     ['Spartacus[oracle]'],
        'mssql':      ['Spartacus[mssql]'],
        'ibmdb2':     ['Spartacus[ibmdb2]'],
        'complete':   ['Spartacus[complete]']
      },
      zip_safe=False)
