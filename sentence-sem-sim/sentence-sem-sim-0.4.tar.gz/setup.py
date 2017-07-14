from setuptools import setup
setup(
  name = 'sentence-sem-sim',
  packages = ['sentence-sem-sim'], # this must be the same as the name above
  version = '0.4',
  description = 'Sentence Semantic Similarity in Python.',
  author = 'Shaun Chiang',
  author_email = 'redbeansodapop@hotmail.com',
  url = 'https://github.com/shaun-chiang/sentence-sem-sim/tree/master', # use the URL to the github repo
  keywords = ['sentence', 'semantic', 'similarity'], # arbitrary keywords
  classifiers = [],
  license='MIT',
  install_requires=['nltk>=3.2.1',
                    'numpy>=1.11']
)