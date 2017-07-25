from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(name='hinomaru',
      version=version,
      description="useful library",
      long_description="""\
useful library for making web application""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Katolele',
      author_email='katolele@katolele.net',
      url='http://katolele.net/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
