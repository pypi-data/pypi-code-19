from distutils.core import setup

setup(
  name = 'igdb_api_python',
  packages = ['igdb_api_python'], # this must be the same as the name above
  version = '0.302',
  description = 'Python wrapper for IGDB.com API',
  author = 'Sander Brauwers',
  author_email = 'sander.brauwers@igdb.com',
  url = 'https://github.com/igdb/igdb_api_python', # use the URL to the github repo
  download_url = 'https://github.com/igdb/igdb_api_python/releases/tag/0.21.tar.gz', # I'll explain this in a second
  keywords = ['igdb', 'videogame', 'api','database'], # arbitrary keywords
  classifiers = [],
  install_requires=[
      'requests>=2.18.1',
  ],
)
