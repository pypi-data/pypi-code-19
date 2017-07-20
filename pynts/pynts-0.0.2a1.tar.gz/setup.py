"""
BSD 3-Clause License

Copyright (c) 2017, Gilberto Pastorello
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

pynts setup

@author: Gilberto Pastorello
@contact: gzpastorello@lbl.gov
@date: 2017-07-17
"""
import os
import setuptools

import pynts

curdir = os.path.abspath(os.path.dirname(__file__))

long_description = """**pynts**

**pynts (Python Naive Time Series)** is a set of simple utility tools for handling timeseries data

pynts github page:
https://github.com/gilbertozp/pynts


**Contributors**

- Gilberto Pastorello, gzpastorello@lbl.gov, 20170717
"""


setuptools.setup(
    name=pynts.__name__,
    version=pynts.__version__,
    description=pynts.__description__,
    long_description=long_description,
    url='https://github.com/gilbertozp/pynts',
    author=pynts.__author__,
    author_email=pynts.__email__,
    license=pynts.__license__,

    # https://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        # 'Development Status :: 1 - Planning',
        'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',

        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        # 'Programming Language :: Python :: 3.6',

    ],

    keywords='simple time series tools',
    packages=setuptools.find_packages(curdir, exclude=['docs']),

    install_requires=[
        'numpy',
        'matplotlib',
        'scipy',
        'pytest',
        'testfixtures',
    ],

    scripts=['runpynts']
)
