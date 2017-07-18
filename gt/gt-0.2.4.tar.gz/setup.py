#!/usr/bin/env python3

from distutils.core import setup
setup(name='gt',
      version='0.2.4',
      author='Raheman Vaiya',
      author_email='r.vaiya@gmail.com',
      url='http://gitlab.com/rvaiya/gt',
      packages=['gt.sources'],
      keywords='git github gitlab ssh cli console management',
      long_description=open('README.rst').read(),
      scripts=['bin/gt'],
      classifiers=[
          'Programming Language :: Python :: 3',
          'Development Status :: 3 - Alpha'
      ]
)
