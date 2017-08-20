# -*- coding: utf-8 -*-
"""
Created on Sun Aug 20 13:49:47 2017

@author: Xeobo
"""

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='humanactivity',
      version='0.1',
      description='Human activity recognizer based on keras and thensorflow',
      long_description=readme(),
      url='http://github.com/XEOBO/HumanActivity',
      author='Vladimir Zbiljic',
      author_email='vladimir.zbiljic@gmail.com',
      license='MIT',
      packages=['humanactivity'],
      include_package_data=True,
      install_requires=[
              'numpy', 'pandas', 'enum', 'threading', 'time', 'sklearn',
              'keras'
      ],
      zip_safe=False)