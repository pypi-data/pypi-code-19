from setuptools import setup, find_packages
setup(
  name = 'oglhclient',
  version = '0.1.8.8.3',
  description = 'A client for Lighthouse API',
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
