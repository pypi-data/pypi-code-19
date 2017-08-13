"""
setup.py script for MakeItSo

For packaging info please see:
https://docs.python.org/2/distutils/sourcedist.html
"""
# https://github.com/nipy/nipype/blob/master/setup.py
# might also be helpful

import os
from setuptools import setup

try:
    here = os.path.dirname(os.path.abspath(__file__))
    description = open(os.path.join(here, 'README.txt')).read()
except IOError:
    description = ''

version = '0.6'

setup(name='MakeItSo',
      version=version,
      description='filesystem template interpreter',
      long_description=description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='templates',
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/hg/MakeItSo',
      license='MPL',
      packages=['makeitso'],
      include_package_data=True,
      package_data={'makeitso': [
          os.path.join('python_package', 'tests', '*')
      ]},
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'tempita >= 0.5.1',
          'webob',
      ],
      tests_require=['tox', 'pytest'],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      makeitso = makeitso.makeitso:main
      make-python-package = makeitso.python:main
      mkpydir = makeitso.mkpydir:main
      script2package = makeitso.script2package:main
      file2template = makeitso.file2template:main

      [makeitso.templates]
      python-package = makeitso.python:PythonPackageTemplate
      python-module = makeitso.python:PythonModuleTemplate
      python-script = makeitso.python:PythonScriptTemplate
      setup.py = makeitso.python:SetupPy
      python-unittest = makeitso.python:Unittest
      """,
      )
