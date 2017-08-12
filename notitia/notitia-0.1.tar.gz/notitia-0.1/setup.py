#from distutils.core import setup
from setuptools import setup
setup(
  name = 'notitia',
  py_modules = ['notitia'], # this must be the same as the name above
  version = '0.1',
  description = 'Tool for preparing dataset for Image Recognition',
  author = 'Prashant Kumar',
  author_email = 'prashant.kiit2018@gmail.com',
  url = 'https://github.com/prashant2018/notitia', # use the URL to the github repo
  download_url = 'https://github.com/prashant2018/notitia/archive/0.1.tar.gz', # I'll explain this in a second
  keywords = ['tool', 'machine learning', 'open', 'source'], # arbitrary keywords
  install_requires=[
          'cycler',
          'decorator',
          'matplotlib',
          'networkx',
          'numpy',
          'olefile',
          'Pillow',
          'pyparsing',
          'python-dateutil',
          'pytz',
          'PyWavelets',
          'scikit-image',
          'scipy',
          'six',
      ],
  classifiers = [],
)
