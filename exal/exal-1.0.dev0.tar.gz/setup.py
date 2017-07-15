from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='exal',
      version=version,
      description="Excel abstraction layer",
      long_description="""
      Abstraction layer for multible Excel wrapper.
      Supports:
       - win32com
       - xlwings
       - comtype
       - openpyxl
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
       keywords=['xls', 'excel', 'spreadsheet', 'workbook'],
      author='Kevin Gliewe',
      author_email='kevingliewe@gmail.com',
      url='https://github.com/KevinGliewe/exal',
      license='',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'openpyxl',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )