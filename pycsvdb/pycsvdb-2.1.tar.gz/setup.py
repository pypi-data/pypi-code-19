from setuptools import setup
from codecs import open
from os import path
here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='pycsvdb',
      version='2.1',
      description='Reading CSV file and insert into database',
      long_description=long_description,
      url='https://github.com/sajeeshe/python-csv-easy',
      author='Sajeesh E Namboothiri',
      author_email='sajeeshe@gmail.com',
      license='MIT',
      packages=['pycsvdb'],
      keywords='CSV database pandas',
      zip_safe=False)
