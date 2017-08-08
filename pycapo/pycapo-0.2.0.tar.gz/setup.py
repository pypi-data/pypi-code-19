# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

NAME = 'pycapo'
HERE = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(HERE, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(HERE, 'CHANGES.txt')) as f:
    CHANGES = f.read()
with open(os.path.join(HERE, NAME, '_version.py')) as f:
    VERSION = f.readlines()[-1].split()[-1].strip("\"'")

INST_REQUIRES = []
TEST_REQUIRES = ['pytest==3.0.5']
SETUP_REQUIRES = ['pytest-runner==2.9']

setup(name=NAME,
      version=VERSION,
      description='CAPO (CASA, Archive, and Pipeline Options) for Python',
      long_description=README + '\n\n' + CHANGES,
      author='Stephan Witz',
      author_email='switz@nrao.edu',
      url='https://open-bitbucket.nrao.edu/projects/SSA/repos/pycapo',
      keywords='',
      license='GPL',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',

          # probably not the best topic, unsure what else to puy here
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='pycapo.tests',
      install_requires=INST_REQUIRES,
      tests_require=TEST_REQUIRES,
      setup_requires=SETUP_REQUIRES,
      entry_points={
          'console_scripts': [
              'pycapo = pycapo.commands:pycapo'
          ]
      },
      )
