from setuptools import setup
import codecs
import os
import re

import floppy

HERE = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    return codecs.open(os.path.join(HERE, *parts), 'r').read()

LONG_DESCRIPTION = read('README.md')

setup(
    name='floppy',
    version=floppy.__version__,
    url='http://github.com/vndmtrx/floppy/',
    license='Apache License 2.0',
    author='Eduardo Rolim',
    install_requires=[],
    author_email='vndmtrx@gmail.com',
    description='Python Powered Static Site Generation Tool',
    long_description=LONG_DESCRIPTION,
    #entry_points={
    #    'console_scripts': [
    #        'floppyctl = floppy.scripts.floppyctl:main',
    #        ],
    #    },
    packages=['floppy'],
    include_package_data=True,
    platforms='any',
    classifiers=[ #https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 1 - Planning',
        'Natural Language :: Portuguese (Brazilian)',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Build Tools',
        ],
)
