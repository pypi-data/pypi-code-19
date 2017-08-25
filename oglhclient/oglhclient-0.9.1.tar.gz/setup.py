import io
import pypandoc
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Translate oglhclient README.md to .rst
long_description = pypandoc.convert_file(path.join(here, 'oglhclient/README.md'), 'rst')

setup(
  name = 'oglhclient',
  version = '0.9.1',
  description = 'A client for Lighthouse API',
  long_description=long_description,
  author = 'Lighthouse Team',
  author_email = 'engineering@opengear.com',
  url = 'https://github.com/opengeardev/oglhclient',
  download_url = 'https://github.com/opengeardev/oglhclient/archive/0.9.tar.gz',
  keywords = ['api', 'opengear', 'lighthouse'],
  classifiers = ['Programming Language :: Python :: 3', 'Programming Language :: Python :: 2'],
  install_requires = ['requests','urllib','pyyaml','future', 'pypandoc'],
  packages=find_packages(),
  package_data={'': ['*.raml', '*.html']},
)
