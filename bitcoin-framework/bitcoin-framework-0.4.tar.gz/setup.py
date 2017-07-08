from setuptools import setup, find_packages
setup(
  name = 'bitcoin-framework',
  packages = find_packages(),
  version = '0.4',
  description = 'Python Bitcoin framework to create transactions with smart contracts based on puzzle-friendliness and OOP principles',
  license = 'Apache License v2.0',
  author = 'UAB Projects Team: davidlj95 & ccebrecos',
  author_email = 'mail@uab.codes',
  url = 'https://github.com/uab-projects/bitcoin-framework',
  download_url = 'https://github.com/uab-projects/bitcoin-framework/archive/0.4.tar.gz',
  keywords = ['bitcoin', 'bitcoin framework', 'bitcoin-framework','bitcoin api','bitcoin-api'],
  install_requires=['python-bitcoinlib','bitcoin'],
  classifiers = []
)
