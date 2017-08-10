from setuptools import setup, find_packages
setup(
  name = 'qspin',
  packages = find_packages(),
  version = '0.1.8',
  description = 'Learn quantum spin and entanglement',
  author = 'Don Gavel',
  author_email = 'donald.gavel@gmail.com',
  url = 'https://bitbucket.org/donald_gavel/qspin', # the github repo
  install_requires=[
    'numpy',
  ],
  download_url = 'https://bitbucket.org/donald_gavel/qspin/downloads',
  keywords = ['quantum', 'spin', 'electron'], # arbitrary keywords
  classifiers = [],
)
# 
