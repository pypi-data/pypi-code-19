#!/usr/bin/env python

from setuptools import setup

setup(name='mzgtfs-tools',
      version='0.1.2',
      description='tools using mapzen-gtfs library',
      author='Tony Laidig',
      author_email='laidig@gmail.com',
      url='https://github.com/BusTechnology/mzgtfs-tools',
      packages=['mzgtfs-tools'],
      install_requires=[
          'plac==0.9.6', 
          'mzgtfs'
          ],
      dependency_links = [
          'http://github.com/BusTechnology/mapzen-gtfs.git#egg=mzgtfs-tools'
      ],
      license='Apache',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7'
    ]
)
