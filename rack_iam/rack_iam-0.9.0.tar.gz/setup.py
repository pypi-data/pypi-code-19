# -*- coding: utf-8 -*-
# Copyright 2017 Rackspace US, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The setup.py file for Rack IAM."""
from setuptools import setup, find_packages
import unittest

DEPENDENCIES = []

TESTS_REQUIRE = []


def my_test_suite():
    """Initialize the test suite for `setup.py`.

    This makes it so that when `python setup.py test` runs it will utilize the
    unit tests in the `tests` folder.
    """
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


setup(
    name='rack_iam',
    description='A framework for AWS IAM components',
    keywords=['troposphere', 'rackspace', 'iam', 'aws'],
    version='0.9.0',
    tests_require=TESTS_REQUIRE,
    install_requires=DEPENDENCIES,
    extras_require={
        'docs': [
            'sphinx'
        ]
    },
    include_package_data=True,
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Security',
        'Topic :: System :: Systems Administration'
    ],
    license='Apache License 2.0',
    author='Chris White',
    maintainer_email='chris.white@rackspace.com',
    url='https://github.com/rackerlabs/rack_iam_oss',
    test_suite='setup.my_test_suite'
)
