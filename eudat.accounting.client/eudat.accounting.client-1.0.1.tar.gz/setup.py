# -*- coding: utf-8 -*-
"""\
=======================
eudat.accounting.client
=======================

Upload accounting records to an eudat accounting server
"""

from setuptools import setup, find_packages
import os, sys

version = '1.0.1'

this_directory = os.path.abspath(os.path.dirname(__file__))

def read(*names):
    return open(os.path.join(this_directory, *names), 'r').read().strip()

long_description = '\n\n'.join(
    [read(*paths) for paths in (('README.rst',),('CHANGES.rst',))]
    )
dev_require = []
if sys.version_info < (2, 7):
    dev_require += ['unittest2']


setup(name='eudat.accounting.client',
      version=version,
      description="Upload accounting records to an eudat accounting server",
      long_description=long_description,
      classifiers=[
          "Environment :: Console",
          "Intended Audience :: System Administrators",
          "Programming Language :: Python :: 2.7",
          "Operating System :: OS Independent",
          "License :: OSI Approved :: BSD License",
          "Topic :: Utilities",
          ],
      keywords=['EUDAT', 'storage', 'accounting', 'comamndline', 'client'],
      author='Raphael Ritz',
      author_email='raphael.ritz@gmail.com',
      url='https://github.com/raphael-ritz/eudat.accounting.client',
      license='BSD',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['eudat', 'eudat.accounting'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # 3rd party
          'setuptools',
          'requests',
          ],
      entry_points={
          'console_scripts': [
              'addRecord=eudat.accounting.client.__main__:main',
              'iRODScollector=eudat.accounting.client.iRODScollector:main',
          ]
          },
      tests_require=dev_require,
      test_suite='tests.all_tests',
      extras_require={
          'dev': dev_require
      })
