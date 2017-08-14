
from setuptools import setup, find_packages
setup(
  name = 'oglhslack',
  version = '0.1.4.1',
  description = 'A Slack bot client for Lighthouse API',
  author = 'Lighthouse Team',
  author_email = 'engineering@opengear.com',
  url = 'https://github.com/thiagolcmelo/oglhslack',
  download_url = 'https://github.com/thiagolcmelo/oglhslack/archive/0.1.4.1.tar.gz',
  keywords = ['api', 'opengear', 'lighthouse', 'slackbot'],
  classifiers = ['Programming Language :: Python :: 2'],
  install_requires = ['pyyaml', 'slackclient', 'oglhclient', 'requests', 'urllib', 'future'],
  packages=find_packages(),
)
