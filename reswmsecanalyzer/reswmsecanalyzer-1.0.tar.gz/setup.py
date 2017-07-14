#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='reswmsecanalyzer',
      version='1.0',
      description='A simple script to visualize and find bypasses in RES Workspace Manager application restrictions',
      url='https://github.com/maaaaz/reswmsecanalyzer',
      author='Thomas D.',
      author_email='tdebize@mail.com',
      license='LGPL',
      classifiers=[
        'Topic :: Security',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Information Technology',
        'Programming Language :: Python :: 2 :: Only',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
      ],
      keywords='res workspace manager restrictions',
      packages=find_packages(),
      install_requires=['networkx', 'matplotlib'],
      python_requires='<3',
      entry_points = {
        'console_scripts': ['reswmsecanalyzer=reswmsecanalyzer.reswmsecanalyzer:main'],
      },
      include_package_data=True)