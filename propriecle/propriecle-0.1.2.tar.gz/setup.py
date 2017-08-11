#!/usr/bin/env python
import os
import sys
from setuptools import setup
from pkg_resources import resource_filename

# depending on your execution context the version file
# may be located in a different place!
vsn_path = resource_filename(__name__, 'propriecle/version')
if not os.path.exists(vsn_path):
    vsn_path = resource_filename(__name__, 'version')
    if not os.path.exists(vsn_path):
        print("%s is missing" % vsn_path)
        sys.exit(1)


setup(name='propriecle',
      version=open(vsn_path, 'r').read(),
      description='something something vault master keys',
      author='Jonathan Freedman',
      author_email='jonathan.freedman@autodesk.com',
      license='MIT',
      url='https://github.com/autodesk/propriecle',
      install_requires=['PyYAML', 'hvac', 'future', 'cryptorito'],
      include_package_data=True,
      packages=['propriecle'],
      entry_points={
          'console_scripts': ['propriecle = propriecle.cli:main']
      },
      package_data={'propriecle': ['version']}
)
