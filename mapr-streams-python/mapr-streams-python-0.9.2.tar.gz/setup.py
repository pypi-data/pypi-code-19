#!/usr/bin/env python

from setuptools import setup, find_packages
from distutils.core import Extension


module = Extension('mapr_streams_python.cimpl',
                    libraries= ['rdkafka'],
                    sources=['mapr_streams_python/src/mapr_streams_python.c',
                             'mapr_streams_python/src/Producer.c',
                             'mapr_streams_python/src/Consumer.c'])

setup(name='mapr-streams-python',
      version='0.9.2',
      description='MapR Streams Python Client',
      author='Confluent & MapR',
      author_email='support@mapr.com',
      url='https://github.com/mapr/confluent-kafka-python',
      license='Apache 2.0',
      ext_modules=[module],
      packages=find_packages(),
      data_files = [('', ['LICENSE'])])
