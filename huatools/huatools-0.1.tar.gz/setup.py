import os
import glob
import sys
from setuptools import setup, find_packages

setupargs = {}

setup(name='huatools',
      version='0.1',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      #scripts = glob.glob('src\\scripts\\*.py'),
      py_modules = ['huaexcel', 'huasap', 'huanexus'],

      # dependencies:
      install_requires = ['xlrd', 'xlsxwriter', 'apsw', 'regex', "pycountry", "roman"],

      # PyPI metadata
      author='Danian Hu',
      author_email='hudanian@gmail.com',
      description='Hua Quotation projects',
      **setupargs
     )
