import giphypy
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

setup(**setup_kwargs)
