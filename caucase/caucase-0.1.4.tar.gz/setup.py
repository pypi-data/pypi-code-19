# This file is part of caucase
# Copyright (C) 2017  Nexedi
#     Alain Takoudjou <alain.takoudjou@nexedi.com>
#     Vincent Pelletier <vincent@nexedi.com>
#
# caucase is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# caucase is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with caucase.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages
import glob
import os

version = '0.1.4'
name = 'caucase'
long_description = open("README.rst").read() + "\n"

for f in sorted(glob.glob(os.path.join('caucase', 'README.*.rst'))):
  long_description += '\n' + open(f).read() + '\n'

# long_description += open("CHANGES.txt").read() + "\n"

# Provide a way to install additional requirements
additional_install_requires = []
try:
  import argparse
except ImportError:
  additional_install_requires.append('argparse')

setup(name=name,
      version=version,
      description="Certificate Authority.",
      long_description=long_description,
      classifiers=[
          "Programming Language :: Python",
        ],
      keywords='certificate authority',
      url='https://lab.nexedi.com/nexedi/caucase',
      license='GPLv3',
      namespace_packages=['caucase'],
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
        'Flask', # needed by servers
        'flask_user',
        'Flask-AlchemyDumps',
        'setuptools', # namespaces
        'pyOpenSSL', # manage ssl certificates
        'pyasn1', # ASN.1 types and codecs for certificates
        'pyasn1-modules',
        'requests', # http requests
        'pem', # Parse PEM files
      ] + additional_install_requires,
      extras_require = {

      },
      tests_require = [
        'Flask-Testing',
      ],
      zip_safe=False, # proxy depends on Flask, which has issues with
                      # accessing templates
      entry_points={
        'console_scripts': [
          'caucase = caucase.web:start',
          'caucase-cli = caucase.cli:main',
          'caucase-cliweb = caucase.cli_flask:main',
        ]
      },
      test_suite='caucase.test',
    )
