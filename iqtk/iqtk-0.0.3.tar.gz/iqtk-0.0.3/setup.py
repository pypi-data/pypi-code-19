# Copyright 2017 The Regents of the University of California
#
# Licensed under the BSD-3-clause license (the "License"); you may not
# use this file except in compliance with the License.
# You are provided a copy of the license in LICENSE.md at the root of
# this project.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

_VERSION = '0.0.3'

REQUIRED_PACKAGES = [
    "google-cloud-pubsub",
    "google-cloud-dataflow",
    "protobuf",
    "google-cloud-bigquery",
    "docker",
    "subprocess32",
    "uritemplate",
    "coloredlogs",
    "google-api-python-client",
    "click",
    "flask"
]

project_name = 'iqtk'
CONSOLE_SCRIPTS = ['iqtk = inquiry.framework.cli:main',
                   'iq-serv = inquiry.services.run:main']
TEST_PACKAGES = []

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name=project_name,
    version=_VERSION,
    description='Reproducible biological data science.',
    long_description='The Inquiry Toolkit is a full stack of open-source data infrastructure components for reproducible scientific research.',
    url='http://iqtk.io',
    author='University of California',
    author_email='inquiryproject@lists.lbl.gov',
    packages=find_packages(),
    entry_points={
        'console_scripts': CONSOLE_SCRIPTS,
    },
    install_requires=REQUIRED_PACKAGES,
    tests_require=REQUIRED_PACKAGES + TEST_PACKAGES,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Information Analysis'
        ],
    license='BSD-3',
    keywords='inquiry genom proteom metabolom transcriptom',
    zip_safe=False,
    include_package_data=True,
    )
