from distutils.core import setup
setup(
  name = 'mypack',
  packages = ['mypack'], # this must be the same as the name above
  version = '0.1',
  description = 'A random test lib',
  author = 'Chirag',
  author_email = 'chirag.intern@reverieinc.com',
  url = 'https://github.com/chirag-b/test.git', # use the URL to the github repo
  download_url = 'https://github.com/chirag-b/test/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['testing', 'logging', 'example'], # arbitrary keywords
  classifiers = [],
)