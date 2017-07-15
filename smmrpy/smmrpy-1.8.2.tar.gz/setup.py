import os
import sys

from distutils.core import setup

# Thanks Laura
rootpath = os.path.abspath(os.path.dirname(__file__))
def extract_version(module = 'smmrpy'):
    version = None
    fname = os.path.join(rootpath, module, '__init__.py')
    with open(fname) as f:
        for line in f:
            if line.startswith('__version__'):
                _, version = line.split('=')
                version = version.strip()[1:-1]  # Remove quotation characters.
                break
    return version

version = extract_version()

setup(
  name = 'smmrpy',
  packages = ['smmrpy'],
  version = version,
  description = 'Async api wrapper for the SMMRY api.',
  author = 'Tyler Gibbs',
  author_email = 'gibbstyler7@gmail.com',
  url = 'https://github.com/TheTrain2000/smmrpy',
  download_url = 'https://github.com/TheTrain2000/smmrpy/archive/{}.tar.gz'.format(version),
  keywords = ['api', 'async', 'smmry', 'wrapper'],
  classifiers = [],
)
