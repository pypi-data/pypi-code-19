# New 2017 using setuptools instead of distutils
from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

readme = read('README.rst')

setup(name='sc14npy',
      version='0.9.0rc3',
      description='A Python interface to SC14N',
      long_description=readme,
      author='David Ireland',
      url='http://www.di-mgt.com.au/sc14n/',
      platforms=['Windows'],
      py_modules=['sc14n'],
      )
