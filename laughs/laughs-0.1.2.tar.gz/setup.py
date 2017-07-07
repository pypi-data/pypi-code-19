"""
    setup.py
    ~~~~~~~~

    Package setup file for laughs.

    :copyright: (c) 2017 by Sean Callaway.
    :license: MIT, see LICENSE for more details.
"""
from setuptools import setup

setup(name='laughs',
      version='0.1.2',
      description='Pulls jokes from various APIs',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'License :: OSI Approved :: MIT License',
          'Topic :: Games/Entertainment :: Fortune Cookies' ],
      url='https://github.com/seancallaway/laughs',
      author='Sean Callaway',
      author_email='seancallaway@gmail.com',
      license='MIT',
      packages=['laughs', 'laughs.services'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)
