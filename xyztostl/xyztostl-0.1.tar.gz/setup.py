from setuptools import setup
setup(
  name = 'xyztostl',
  packages = ['xyztostl'], # this must be the same as the name above
  version = '0.1',
  description = 'A library that takes points clouds from different file types and converts them into an stl file for printing as best as possible.',
  author = 'Alexander Sludds',
  author_email = 'asludds@mit.edu',
  url = 'https://github.com/alexsludds/xyztostl', # use the URL to the github repo
  download_url = 'https://github.com/alexsludds/xyztostl/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['printing', 'stl', 'points'], # arbitrary keywords
  classifiers = [
   'Development Status :: 3 - Alpha',
   'Programming Language :: Python :: 3.5'
  ],
)