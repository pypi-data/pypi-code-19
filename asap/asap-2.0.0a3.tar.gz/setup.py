#!/usr/bin/env python3

import sys
import platform
import setuptools

if not platform.python_version().startswith('3'):
  sys.stdout.write("Please use Python 3!\n")
  sys.exit(-1)

def readme():
  with open('README', 'wb') as of:
    with open('README.rst', 'rb') as i:
      out = b''.join([ line for line in i if not line.startswith(b'[')])
      of.write(out)
      return out.decode('utf8')

setuptools.setup(name='asap',
      version='2.0.0a3',
      description='ASAP Answer Set Application Programming',
      long_description=readme(),
      classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Utilities',
      ],
      url='https://github.com/hexhex/hexlite',
      author='Peter Schuller, Antonius Weinzierl',
      author_email='schueller.p@gmail.com',
      license='BSD',
      packages=['asap', 'asap.core', 'asap.plugins', 'asap.examples', 'asap_tetris', 'asap_aplagent'],
      package_data = {
        'asap.core' : ['*.jar'],
        'asap.examples' : ['*.asap'],
        'asap-tetris' : ['*.asap', 'resources/*.png'],
        'asap-aplagent' : ['*.asap', '*.apl'],
      },
      scripts=[
        'bin/asap',
        'bin/asap-aplagent',
        'bin/asap-tetris',
        'bin/asap-example-onoffswitch',
      ],
      zip_safe=False)
