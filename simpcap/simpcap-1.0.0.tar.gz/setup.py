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
    name="simpcap",
    description='PCAP parser for the command line. Built on Python and Click.',
    long_description='''
    Simpcap is a PCAP parser that lists basic information about specific packets in a PCAP file.
    Simpcap checks the source and destination ports, layers, and TLS (or SSL) version for each packet.
    Simpcap will display certain packets based on what flags and options are provided when the parser is executed.
    Simpcap can output the results to the command line or to a TXT file.
    ''',
    author='Alex Hadi',
    url='https://github.com/hadi16/simpcap',
    version='1.0.0',
    license='Apache License, Version 2.0',
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Security',
    ],
    packages=find_packages(),
    py_modules=['__init__'],
    install_requires=['click', 'pyshark'],
    python_requires='==2.7.*',
    entry_points='''
        [console_scripts]
        simpcap=simpcap:cli
    ''',
)
