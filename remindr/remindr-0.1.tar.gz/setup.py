# Copyright 2017 Carl Chenet <carl.chenet@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#!/usr/bin/env python3

# Setup for Remindr
'''Setup for Remindr'''

from setuptools import setup, find_packages

CLASSIFIERS = [
    'Intended Audience :: End Users/Desktop',
    'Environment :: Console',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6'
]


setup(
    name='remindr',
    version='0.1',
    license='GNU GPL v3',
    description='Automatically send toots/tweets to remind people about the last blog entries on social networks',
    long_description='Automatically get data from a list and send messages to social networks to remind people about the most interesting blog posts you wrote',
    author = 'Carl Chenet',
    author_email = 'chaica@ohmytux.com',
    url = 'https://gitlab.com/chaica/remindr',
    classifiers=CLASSIFIERS,
    download_url='https://gitlab.com/chaica/remindr',
    packages=find_packages(),
    scripts=['scripts/remindr', 'scripts/register_remindr_app'],
    install_requires=['Mastodon.py', 'tweepy'],
)
