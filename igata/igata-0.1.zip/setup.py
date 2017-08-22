#!/usr/bin/env python

from distutils.core import setup

setup(name='igata',
      version='0.1',
      packages=['igata'],
      scripts=['bin/igata', 'bin/igata.cmd'],
      description='JEE Domain Tool and DSL',
      long_description='Java EE domain generation tool with nifty DSL',
      url='https://github.com/katthjul/igata',
      author='Pauline Gomér',
      author_email='pauline.gomer@gmail.com',
      maintainer='Jon-Erik Johnzon',
      maintainer_email='jone@torrentkatten.se',
      license='MIT'
     )
