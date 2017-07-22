#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='snspoliciestocsv',
      version='1.1',
      description='A simple script to extract policies from a Stormshield Network Security device configuration file to CSV',
      long_description=open('snspoliciestocsv/README.md').read(),
      url='https://github.com/maaaaz/snspoliciestocsv',
      author='Thomas D.',
      author_email='tdebize@mail.com',
      license='LGPL',
      classifiers=[
        'Topic :: Security',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
      ],
      keywords='stormshield network security configuration csv',
      packages=find_packages(),
      python_requires='>=3',
      entry_points = {
        'console_scripts': ['snspoliciestocsv=snspoliciestocsv.snspoliciestocsv:main'],
      },
      include_package_data=True)