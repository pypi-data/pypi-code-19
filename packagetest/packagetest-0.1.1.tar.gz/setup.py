# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='packagetest',
    version='0.1.1',
    description='Sample package for Python-Guide.org',
    long_description=readme,
    author='Jeff Richard',
    author_email='jeff@jeffrichard.com',
    url='https://github.com/jeffrichard/wiab',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
          'spidev',
      ],

    dependency_links=['https://github.com/doceme/py-spidev.git']

)
