import io
from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with io.open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'oglhslack',
  version = '0.1.4.4',
  description = 'A Slack bot client for Lighthouse API',
  long_description=long_description,
  author = 'Lighthouse Team',
  author_email = 'engineering@opengear.com',
  url = 'https://github.com/thiagolcmelo/oglhslack',
  download_url = 'https://github.com/thiagolcmelo/oglhslack/archive/0.1.4.4.tar.gz',
  keywords = ['api', 'opengear', 'lighthouse', 'slackbot'],
  classifiers = [
    'Development Status :: 3 - Alpha',
    "Intended Audience :: Developers",
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3'
  ],
  install_requires = ['pyyaml', 'slackclient', 'oglhclient', 'requests', 'urllib', 'future'],
  packages=find_packages(),
)
