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

_VERSION = '0.0.2'


REQUIRED_PACKAGES = [
    # 'google-cloud-dataflow',
    # 'click',
    # 'docker',
    #'colorama',
    # 'coloredlogs',
    # 'google-apitools',
    # 'google-auth',
    # 'google-gax',
    # 'grpcio',
    # 'oauth2client',
    # 'protobuf',
    # 'pytest',
    # 'pytz',
    # 'PyYAML',
    # 'requests',
    # 'rsa',
    # 'six',
    # 'subprocess32',
    # 'uritemplate'
    'google-cloud-dataflow==0.6.0',
    'google-cloud-bigquery==0.22.1',
    'google-api-python-client==1.6.2',
    'click==6.7',
    'docker==2.2.1',
    'colorama==0.3.9',
    'coloredlogs==6.1',
    'google-apitools==0.5.10',
    'google-auth==1.0.0',
    'google-auth-httplib2==0.0.2',
    'google-cloud-core==0.22.1',
    'google-gax==0.15.8',
    'googleapis-common-protos==1.5.2',
    'grpcio==1.2.1',
    'oauth2client==3.0.0',
    'proto-google-cloud-datastore-v1==0.90.0',
    'proto-google-cloud-logging-v2==0.91.3',
    'protobuf==3.2.0',
    'pytest==3.0.7',
    'pytest-cov==2.4.0',
    'pytz==2017.2',
    'PyYAML==3.12',
    'requests==2.13.0',
    'rsa==3.4.2',
    'six==1.10.0',
    'subprocess32==3.2.7',
    'uritemplate==3.0.0',
]

project_name = 'iqtk'

CONSOLE_SCRIPTS = [
    'iqtk = inquiry.framework.cli:main'
    ]

TEST_PACKAGES = [
    # 'pytest',
    # 'pytest-cov'
]
#
# TEST_ARGS = [
#     '--cov-report=term',
#     '--cov-report=html',
#     '--cov=inquiry'
# ]

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# class IQTKTest(TestCommand):
#     user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]
#
#     def initialize_options(self):
#         TestCommand.initialize_options(self)
#
#     def run_tests(self):
#         import pytest
#         errno = pytest.main(TEST_ARGS + self.get_subtest())
#         sys.exit(errno)
#
#     def get_subtest(self):
#         return []
#
#
# class UnitTest(IQTKTest):
#
#     def get_subtest(self):
#         return ['inquiry']

setup(
    name=project_name,
    version=_VERSION,
    description='A bioinformatics toolkit.',
    long_description='A toolkit. For *bioinformatics*. Oh yeah.',
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
    # test_suite='test',
    # cmdclass={
    #     'unit': UnitTest
    #     }
    )
