from distutils.core import setup
import pypandoc

#~ ld = pypandoc.convert('README.md', 'rst')

setup(
  name = 'pySkroutz',
  packages = ['pySkroutz'],
  version = '0.0.1.6',
  description = 'Unofficial Python SDK for Skroutz.gr API. This client library is designed to support the Skroutz API. You can read more about the Skroutz API by accessing its official documentation.',
  long_description = open('README.rst').read(),
  author = 'Panagiotis Simakis',
  license = 'GPL',
  author_email = 'simakis@autistici.org',
  url = 'https://github.com/sp1thas/pySkroutz',
  download_url = 'https://github.com/sp1thas/pySkroutz/archive/0.0.1.6.tar.gz',
  keywords = ['skroutz', 'python-sdk', 'sdk', 'api'],
  classifiers = [],
  install_requires=[
        'requests'
    ],
)
