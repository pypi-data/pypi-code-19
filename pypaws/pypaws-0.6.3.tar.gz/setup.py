"""
paws setup module
---- ----- ------
from https://packaging.python.org/distributing/
"""

#from setuptools import setup, find_packages
# To use a consistent encoding
#from codecs import open

from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here,'README.rst')) as f:
    long_description = f.read()

# Executing paws_config.py defines __version__ 
with open(path.join(here,'paws/paws_config.py')) as f: 
    exec(f.read())

__authorship__=''
here = path.abspath(path.dirname(__file__))

with open(path.join(here,'contributors.txt')) as f: 
    for line in f.readlines():
        __authorship__ += line.strip()+', '
__authorship__ = __authorship__[:-2]


setup(
    name='pypaws',

    # Versions should comply with PEP440.  
    version=__version__,

    description='the Platform for Automated Workflows by SSRL',
    long_description=long_description,

    url='https://github.com/slaclab/paws/',
    author=__authorship__,
    author_email='paws-developers@slac.stanford.edu',
    license='BSD',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[

        'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',

        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',

        # Pick your license as you wish (should match "license" above)
        'License :: Public Domain',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.7',
    ],

    keywords='data analysis workflow',

    packages=find_packages(exclude=[]),
    #py_modules=["my_module"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=['pyyaml','pyside'],
    python_requires='>=2.6, <3',

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    #extras_require={
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    #package_data={
    #    'sample': ['package_data.dat'],
    #},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('my_data', ['data/data_file'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # TODO: entry point for paws python console
    entry_points={
        'console_scripts': [
            'paws=paws:main',
        ],
    },
)
