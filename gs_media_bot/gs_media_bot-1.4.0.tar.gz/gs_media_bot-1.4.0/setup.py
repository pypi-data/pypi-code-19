#!/usr/bin/env python3
# pylint: disable=missing-docstring
import codecs
from setuptools import setup
try:
    codecs.lookup('mbcs')
except LookupError:
    def func(name, enc=codecs.lookup('ascii')):
        return {True: enc}.get(name == 'mbcs')
    codecs.register(func)


setup(name='gs_media_bot',
      version='1.4.0',
      description='Bot for posting media to GNU Social.',
      long_description=open('README.rst').read(),
      author='dtluna',
      author_email='dtluna@openmailbox.org',
      maintainer='dtluna',
      maintainer_email='dtluna@openmailbox.org',
      license='GPLv3',
      classifiers=[
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
      ],
      url='https://source.hreopunch.io/dtluna/gs_media_bot',
      platforms=['any'],
      install_requires=['gnusocial>=4.0,<5.0', 'pyxdg'],
      scripts=['scripts/gs_media_bot'])
