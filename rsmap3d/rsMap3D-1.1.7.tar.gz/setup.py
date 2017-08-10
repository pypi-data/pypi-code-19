'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
from setuptools import setup, find_packages


setup(name='rsMap3D',
      version='1.1.7',
      description='Python Program to map xray diffraction data into ' + \
                    'reciprocal space map',
      author = 'John Hammonds, Christian Schleputz',
      author_email = 'JPHammonds@anl.gov',
      url = 'https://confluence.aps.anl.gov/display/RSM/SSG_000116+Reciprocal+Space+Mapping',
      packages = find_packages() ,
      include_package_data = True,
      package_data = {'rsMap3D': ['resources/*.xml',],
                      '' : ['LICENSE',]},
      install_requires = ['spec2nexus',
                 'pillow',
                 ],
      license = 'See LICENSE File',
      platforms = 'any',
      scripts = ['Scripts/rsMap3D',
                 'Scripts/rsMap3D.bat'],
      )
