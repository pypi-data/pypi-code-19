"""
Setup for devscripts
"""
from distutils.core import setup

__version__ = '0.1.4'
URL = 'https://github.com/massard-t/devscripts/archive/{}.tar.gz'.format(
    __version__
)
setup(
    name='devscripts',
    packages=['devscripts'],
    version=__version__,
    description='Scripts and functions to use while coding',
    author='Theo Massard',
    author_email='massar_t@etna-alternance.net',
    url='https://github.com/massard-t/devscripts',
    download_url=URL,
    keywords=['scripts', 'functions', 'optimisation'],
    classifiers=[],
)
