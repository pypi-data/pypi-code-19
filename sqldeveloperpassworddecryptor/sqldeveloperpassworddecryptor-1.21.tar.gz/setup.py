#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(name='sqldeveloperpassworddecryptor',
      version='1.21',
      description='A simple script to decrypt stored passwords from the Oracle SQL Developer IDE',
      long_description=open('sqldeveloperpassworddecryptor/README.md').read(),
      url='https://github.com/maaaaz/sqldeveloperpassworddecryptor',
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
      keywords='oracle sqldeveloper password decryptor',
      packages=find_packages(),
      install_requires=['pycryptodomex'],
      python_requires='<3',
      entry_points = {
        'console_scripts': ['sqldeveloperpassworddecryptor=sqldeveloperpassworddecryptor.sqldeveloperpassworddecryptor:main'],
      },
      include_package_data=True)