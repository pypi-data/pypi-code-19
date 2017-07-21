from distutils.core import setup


with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read().splitlines()

setup(
  name = 'igdb_api_python',
  packages = ['igdb_api_python'], # this must be the same as the name above
  version = '0.22',
  description = 'Python wrapper for IGDB.com API',
  author = 'Sander Brauwers',
  author_email = 'sander.brauwers@igdb.com',
  url = 'https://github.com/igdb/igdb_api_python', # use the URL to the github repo
  download_url = 'https://github.com/igdb/igdb_api_python/releases/tag/0.21.tar.gz', # I'll explain this in a second
  keywords = ['igdb', 'videogame', 'api','database'], # arbitrary keywords
  classifiers = [],
)
