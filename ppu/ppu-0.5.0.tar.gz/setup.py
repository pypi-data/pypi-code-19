#!/usr/bin/env python

from imp import load_source
from os.path import abspath, dirname, join

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

versionpath = join(abspath(dirname(__file__)), "ppu", "__version__.py")
load_source("ppu_version", versionpath)
from ppu_version import __version__  # noqa: ignore flake8 E402

setup(name='ppu',
      version=__version__,
      description='Broytman Portable Python Utilities',
      long_description=open('README.rst', 'rU').read(),
      author='Oleg Broytman',
      author_email='phd@phdru.name',
      url='http://phdru.name/Software/Python/ppu/',
      license='GPL',
      platforms=['any'],
      keywords=[''],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
      ],
      packages=['ppu'],
      scripts=[
          'scripts/cmp.py', 'scripts/remove-old-files.py', 'scripts/rm.py',
          'scripts/which.py',
      ],
      )
