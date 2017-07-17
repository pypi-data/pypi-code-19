#!/usr/bin/env python

from distutils.core import setup

setup(name='os_nova_ha_utils',
      version='1.2.3',
      description='Python Openstack utils package',
      author='Premysl Kouril',
      author_email='pkouril@cra.cz',
      url='http://cra.cz',
      packages=['nova_ha_utils'],
      license='MIT',
      long_description=open('README.md').read(),
      install_requires=[
          'retrying',
          'mdstat'
      ],
      setup_requires=['retrying', 'mdstat'],
      tests_require=['pytest', 'mock'],
     )
