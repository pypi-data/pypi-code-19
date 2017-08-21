import io
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with io.open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'oglhclient',
  version = '0.1.8.8.4.1',
  description = 'A client for Lighthouse API',
  long_description=long_description,
  author = 'Lighthouse Team',
  author_email = 'engineering@opengear.com',
  url = 'https://github.com/thiagolcmelo/oglhclient',
  download_url = 'https://github.com/thiagolcmelo/oglhclient/archive/0.1.8.8.3.tar.gz',
  keywords = ['api', 'opengear', 'lighthouse'],
  classifiers = ['Programming Language :: Python :: 3', 'Programming Language :: Python :: 2'],
  install_requires = ['requests','urllib','pyyaml','future'],
  packages=find_packages(),
  package_data={'': ['*.raml', '*.html']},
)
