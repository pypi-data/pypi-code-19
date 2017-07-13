import giphypy
import sys
from setuptools import setup


version = giphypy.__version__

setup_kwargs = {
    'name': 'giphypy',
    'version': version,
    'url': 'https://github.com/The-PyWaiters/GiphyPy',
    'license': 'MIT',
    'author': 'The PyWaiters',
    'author_email': 'freshjelly12@yahoo.com',
    'description': 'Python Wrapper for Giphy API',
    'packages': ['giphypy'],
    'install_requires': ['aiohttp', 'requests'],
    'keywords': ['web', 'api', 'giphy', 'wrapper'],
    'classifiers': [
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License'
    ],
 }

if sys.version_info < (3, 5):
    """
    If python version is less than 2.5, exit else proceed
    """
    print('\n\033[91m[Error]\033[0m: '
          'giphypy requires Python version >= 3.5.\n\t '
          'You are currently using Python {}\n\t '
          'Exiting...\n'
          .format(sys.version.split('(')[0].strip()))

    sys.exit()

setup(**setup_kwargs)
