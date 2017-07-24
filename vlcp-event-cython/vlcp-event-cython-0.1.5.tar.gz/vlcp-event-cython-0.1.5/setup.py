#!/usr/bin/env python
'''
Created on 2015/11/17

:author: hubo
'''
try:
    import ez_setup
    ez_setup.use_setuptools()
except:
    pass
from setuptools import setup
from distutils.extension import Extension

VERSION = '0.1.5'

import sys
if 'setuptools.extension' in sys.modules:
    m = sys.modules['setuptools.extension']
    try:
        m.Extension.__dict__ = m._Extension.__dict__
    except Exception:
        pass


import glob

setup(name='vlcp-event-cython',
      version=VERSION,
      description='Cython replacement of vlcp.event',
      author='Hu Bo',
      author_email='hubo1016@126.com',
      license="http://www.apache.org/licenses/LICENSE-2.0",
      url='http://github.com/hubo1016/vlcp',
      keywords=['SDN', 'VLCP', 'Openflow'],
      test_suite = 'tests',
      use_2to3=False,
      setup_requires=[
            'setuptools_cython',
            ],
      packages=['vlcp_event_cython'],
      ext_modules=[
            Extension('vlcp_event_cython.event', ['vlcp_event_cython/event.pyx']),
            Extension('vlcp_event_cython.matchtree', ['vlcp_event_cython/matchtree.pyx']),
            Extension('vlcp_event_cython.pqueue', ['vlcp_event_cython/pqueue.pyx'])
            ])


