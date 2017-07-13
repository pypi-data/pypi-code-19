# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A setup module for Open Source Census Instrumentation Library"""

import io
import setuptools


def main():
    long_description = io.open('README.rst', 'rt', encoding='utf-8').read()

    setuptools.setup(
        name='opencensus',
        version='0.0.1',
        description='A stats collection and distributed tracing framework',
        author='OpenCensus Contributors',
        author_email='opencensus-io@googlegroups.com',
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: Implementation :: CPython',
        ],
        long_description=long_description,
        license='Apache-2.0',
        url='https://github.com/census-instrumentation/opencensus-python',
    )


if __name__ == '__main__':
    main()
