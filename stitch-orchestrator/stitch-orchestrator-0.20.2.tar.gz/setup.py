#!/usr/bin/env python

from setuptools import setup

setup(name='stitch-orchestrator',
      version='0.20.2',
      description='Orchestrates streamers and persisters',
      author='Stitch',
      url='https://github.com/stitchstreams/stitch-orchestrator',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['stitch_orchestrator'],
      install_requires=[
          'singer-python==1.6.0',
          'backoff==1.3.2',
          'python-dateutil==2.6.0',
          'requests>=2.12.0',
          'datadog==0.15.0',
          'attrs==16.3.0'
      ],
      entry_points='''
          [console_scripts]
          stitch-orchestrator=stitch_orchestrator:main
      ''',
      packages=['stitch_orchestrator'],
      package_data = {
          'stitch_orchestrator': [
              'logging.conf'
          ]
      },
)
