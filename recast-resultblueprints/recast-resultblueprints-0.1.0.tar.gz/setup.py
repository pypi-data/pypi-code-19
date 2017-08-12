from setuptools import setup, find_packages

setup(
  name = 'recast-resultblueprints',
  version = '0.1.0',
  description = 'recast-resultblueprints',
  url = 'http://github.com/recast-hep/recast-resultblueprints',
  author = 'Lukas Heinrich',
  author_email = 'lukas.heinrich@cern.ch',
  packages = find_packages(),
  include_package_data = True,
  install_requires = [
    'pyyaml'
  ],
  dependency_links = [      
  ]
)
