# Copyright 2017 Alex Hadi
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

from setuptools import setup, find_packages

setup(
    name='WinDeft',
    description='Windows Defender Tester.',
    long_description='''
    WinDeft is a simple command line tester built on Python 2.7.
    WinDeft uses Click for command line functionality.
    WinDeft allows the user to determine whether a given Windows file or folder succeeds or fails a Windows Defender scan.
    ''',
    author='Alex Hadi',
    url='https://github.com/hadi16/windeft',
    version='1.0.0',
    license='Apache License, Version 2.0',
    packages=find_packages(),
    py_modules=['windeft\__init__'],
    install_requires=['click'],
    python_requires='==2.7.*',
    entry_points='''
        [console_scripts]
        windeft=windeft:cli
    ''',
)
