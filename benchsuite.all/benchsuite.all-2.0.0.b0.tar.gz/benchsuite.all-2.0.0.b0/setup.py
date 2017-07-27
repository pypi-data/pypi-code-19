# Benchmarking Suite
# Copyright 2014-2017 Engineering Ingegneria Informatica S.p.A.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Developed in the ARTIST EU project (www.artist-project.eu) and in the
# CloudPerfect EU project (https://cloudperfect.eu/)

from distutils.core import setup
import os


setup(
    name='benchsuite.all',
    version='2.0.0.b0',

    description='A meta-package to install all the benchmarking suite packages',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),

    url='https://github.com/benchmarking-suite/benchsuite-all',

    author='Gabriele Giammatteo',
    author_email='gabriele.giammatteo@eng.it',

    license='Apache',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Topic :: System :: Benchmark',
        'Topic :: Utilities',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Environment :: Console',
        'Operating System :: Unix'
    ],
    keywords='benchmarking cloud testing performance',
    packages=[],
    namespace_packages=['benchsuite'],

    install_requires=['benchsuite.core', 'benchsuite.stdlib', 'benchsuite.rest', 'benchsuite.cli', 'benchsuite.backends']

)