#!/usr/bin/env python2

import sys
import platform
import setuptools

if not platform.python_version().startswith('2'):
  sys.stdout.write("Please use Python 2!\n")
  sys.exit(-1)

def readme():
  with open('README', 'wb') as of:
    with open('README.md', 'rb') as i:
      out = b''.join([ line for line in i if not line.startswith(b'[')])
      of.write(out)
      return out.decode('utf8')

setuptools.setup(name='asap',
      version='2.0.0a1',
      description='ASAP Answer Set Application Programming',
      long_description=readme(),
      classifiers=[
        #'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 2',
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
      author='Peter Schuller/Antonius Weinzierl',
      author_email='schueller.p@gmail.com',
      license='BSD',
      #packages=['asap', 'asap.core'],
      #scripts=['bin/hexlite'],
      zip_safe=False)
