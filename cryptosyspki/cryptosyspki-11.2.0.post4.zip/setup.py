import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


readme = read('README.rst')
changelog = read('CHANGELOG.rst')

setup(name='cryptosyspki',
      version='11.2.0.post4',
      description='Python interface to CryptoSys PKI',
      long_description=readme + '\n\n' + changelog,
      author='David Ireland',
      url='http://www.cryptosys.net/pki/',
      platforms=['Windows'],
      py_modules=['cryptosyspki'],
      )
