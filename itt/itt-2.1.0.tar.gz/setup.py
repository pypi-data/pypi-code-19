
import os
import re
from setuptools import setup, find_packages

MODULE_NAME = u'itt'

metadata_file = open(os.path.join(MODULE_NAME, u'_metadata.py')).read()
metadata = dict(re.findall("__([a-z]+)__\s*=\s*u'([^']+)'", metadata_file))


def read(filename):

    """
    Utility function used to read the README file into the long_description.

    :param filename: Filename to read

    :return: file pointer
    """

    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name=MODULE_NAME,

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=metadata.get(u'version'),

    author=metadata.get(u'author'),
    author_email=metadata.get(u'authoremail'),

    license=metadata.get(u'license'),

    url=metadata.get(u'url'),
    download_url=metadata.get(u'downloadurl'),

    packages=find_packages(),

    # If you want to distribute just a my_module.py, uncomment
    # this and comment out packages:
    #   py_modules=["my_module"],

    description=metadata.get(u'description'),
    long_description=read(u'README.rst'),

    keywords=[],

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project?
        #   Development Status :: 1 - Planning
        #   Development Status :: 2 - Pre-Alpha
        #   Development Status :: 3 - Alpha
        #   Development Status :: 4 - Beta
        #   Development Status :: 5 - Production/Stable
        #   Development Status :: 6 - Mature
        #   Development Status :: 7 - Inactive
        u'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        u'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        u'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        u'Programming Language :: Python :: 2',
        u'Programming Language :: Python :: 2.7',

        u'Topic :: Utilities',
    ],

    # Dependencies
    install_requires=[
        # Some useful third party modules (also required by utilities)
        u'pip>=8.1.2',
        u'better-exceptions>=0.1.6',
        u'requests[security]>=2.11.1',
        u'appdirs>=1.4.0',

        # Our modules (Versions are fixed)
        u'cachingutil==1.0.11',
        u'classutils==1.1.4',
        u'cli_utils==1.0.2',
        u'configurationutil==1.5.3',
        u'conversionutil==1.0.9',
        u'dbhelperutil==1.0.4',
        u'fdutil==1.5.0',
        u'logging-helper==1.5.0',
        # u'macos_tts==0.0.1',  # Enable this when first release is created
        u'misguided_xml==1.0.1',
        u'networkutil==1.9.1',
        u'pydnserver==1.1.3',
        u'pyhttpintercept==0.1.5',
        u'simpil==1.0.1',
        u'stateutil==1.0.10',
        u'tableutil==1.0.14',
        u'timingsutil==1.0.9',
        u'uiutil==1.7.0',
        u'voicerss_tts==1.0.3',

        # Other modules (Not required by utilities, but here for convenience)
        u'websocket-client>=0.37.0',
        u'psutil>=4.3.1',
        u'beautifulsoup4>=4.5.0',
        u'openpyxl>=2.4.0',
    ],

    # Reference any non-python files to be included here
    package_data={
        '': ['*.md', '*.rst', '*.db', '*.txt', '*.json', '*.yaml']
    },

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [],
    },

    # List any scripts that are to be deployed to the python scripts folder
    scripts=[]

)
