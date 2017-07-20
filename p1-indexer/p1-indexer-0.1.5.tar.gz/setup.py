from setuptools import setup, find_packages

setup(
  name = 'p1-indexer',
  packages = find_packages(),
  version = '0.1.5',
  description = 'A package for indexer algolia',
  author = 'Dekoruma',
  author_email = 'hello@dekoruma.com',
  install_requires=[
    'algoliasearch>=1.11,<1.12',
    'Django>=1.9.2,<1.10',
    'django-rq>=0.9.4,<0.10'
  ],
  url = 'https://github.com/jekidekoruma/p1-indexer', # use the URL to the github repo
)
