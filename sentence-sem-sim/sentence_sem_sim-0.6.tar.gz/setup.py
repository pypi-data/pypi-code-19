from setuptools import setup
setup(
  name = 'sentence_sem_sim',
  packages = ['sentence_sem_sim'], # this must be the same as the name above
  version = '0.6',
  description = 'Sentence Semantic Similarity in Python.',
  author = 'Shaun Chiang',
  author_email = 'redbeansodapop@hotmail.com',
  url = 'https://github.com/shaun-chiang/sentence_sem_sim/tree/master', # use the URL to the github repo
  keywords = ['sentence', 'semantic', 'similarity'], # arbitrary keywords
  classifiers = [],
  license='MIT',
  install_requires=['nltk>=3.2.1',
                    'numpy>=1.11'],
  python_requires='>=3',
)