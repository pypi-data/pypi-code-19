from setuptools import setup
from codecs import open  # To use a consistent encoding
from os import path

setup(name='get_nba_data',
      version='1.0.7',
      description='easy tool to load nba data with',
      url='http://github.com/jkim65537/get_nba_data',
      author='Jun Kim',
      author_email='jkim65537@gmail.com',
      license='MIT',
      packages=['get_nba_data'],
      download_url = 'https://github.com/jkim65537/get_nba_data/dist/get_nba_data-1.0.7.tar.gz',
      install_requires=['requests', 'pandas'],
      zip_safe=False)
