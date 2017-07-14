from setuptools import setup
setup(
  name = 'sentence-sem-sim',
  packages = ['sentence-sem-sim'], # this must be the same as the name above
  version = '0.3',
  description = 'Sentence Semantic Similarity in Python.',
  author = 'Shaun Chiang',
  author_email = 'redbeansodapop@hotmail.com',
  url = 'https://github.com/shaun-chiang/sentence-sem-sim/tree/master', # use the URL to the github repo
  download_url = 'https://github.com/shaun-chiang/sentence-sem-sim/archive/0.3.tar.gz', # I'll explain this in a second
  keywords = ['sentence', 'semantic', 'similarity'], # arbitrary keywords
  classifiers = [],
  license='MIT',
  install_requires=['nltk>=3.2.1',
                    'numpy>=1.11']
)