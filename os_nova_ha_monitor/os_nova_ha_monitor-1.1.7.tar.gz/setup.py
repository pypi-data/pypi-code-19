#!/usr/bin/env python

from distutils.core import setup

setup(name='os_nova_ha_monitor',
      version='1.1.7',
      description='Python Openstack Nova HA monitor package',
      author='Premysl Kouril',
      author_email='pkouril@cra.cz',
      url='http://cra.cz',
      packages=['nova_ha_monitor'],
      license='MIT',
      long_description=open('README.md').read(),
      scripts=[
          'scripts/ha_monitor',
          'scripts/health_aggregate',
          'scripts/pick_recovery_target',
          'scripts/runtime_info',
          'scripts/ssh_check',
      ],
      install_requires=[
          'os_nova_ha_utils',
          'python-consul',
          'shade',
          'pyghmi',
          'paramiko',
          'requests',
          'retrying',
          'mdstat'
      ],
      setup_requires=[
          'os_nova_ha_utils',
          'python-consul',
          'shade',
          'pyghmi',
          'paramiko',
          'requests',
          'retrying',
          'mdstat'
      ],
      tests_require=[
          'pytest',
          'mock'
      ],
     )
