from setuptools import setup, find_packages
setup(
  name = 'oglhclient',
  version = '0.1.8.8.0',
  description = 'A client for Lighthouse API',
  author = 'Lighthouse Team',
  author_email = 'engineering@opengear.com',
  url = 'https://github.com/thiagolcmelo/oglhclient',
  download_url = 'https://github.com/thiagolcmelo/oglhclient/archive/0.1.8.8.0.tar.gz',
  keywords = ['api', 'opengear', 'lighthouse'],
  classifiers = [],
  install_requires = ['pyyaml'],
  packages=find_packages(),
  package_data={'': ['*.raml', '*.html']},
)
