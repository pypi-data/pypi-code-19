#!/usr/bin/env python
#==============================================================================

#title           :setup.py
#description     :Build configuration for the project
#author		     :Ajay Krishna Teja Kavuri
#date            :08092017
#version         :0.1
#==============================================================================

# Libraries
from setuptools import setup
#==============================================================================

# Simple readme function for long description
def readme():
    with open('README.rst') as f:
        return f.read()

# Main setup function that helps installing the package
setup(name='kickstart_avs',
      version='0.2.2',
      description='automate avs launch on raspberry pi',
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
      ],
      keywords='alexa avs raspberrypi startup launch',
      url='https://github.com/PseudoAj/kickstart_avs',
      author='Ajay Krishna Teja Kavuri',
      author_email='ajaykrishnateja@gmail.com',
      license='MIT',
      packages=['kickstart_avs'],
      install_requires=[
          'libtmux',
          'sultan',
      ],
      scripts=['bin/kickstart_avs'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
