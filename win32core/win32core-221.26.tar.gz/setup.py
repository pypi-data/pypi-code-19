'''This is a distutils setup-script for the pywin32 extensions

To build the pywin32 extensions, simply execute:
  python setup.py build
or
  python setup.py install
to build and install into your current Python installation.
'''

from setuptools import setup, find_packages, Distribution

# Install all required packages before running anything else
Distribution({
    'setup_requires': [
        'pyyaml',
        'toposort',
        'setuptools_scm',
        'zipfile36;python_version<"3.6"',
    ]
})

import os
import re
import textwrap

from win32.distutils.command import win32_build_ext
from win32.distutils.util import collect_extensions
from distutils.sysconfig import get_config_vars
from contextlib import suppress

# prevent the new in 3.5 suffix of 'cpXX-win32' from being added.
# (adjusting both .cp35-win_amd64.pyd and .cp35-win32.pyd to .pyd)
with suppress(KeyError):
    get_config_vars()["EXT_SUFFIX"] = re.sub("\\.cp\d\d-win((32)|(_amd64))",
                                             "",
                                             get_config_vars()["EXT_SUFFIX"])

setup(
    name='win32core',
    description='Python for Window Extensions',
    long_description=textwrap.dedent('''
        Python extensions for Microsoft Windows'
        Provides access to much of the Win32 API, the
        ability to create and use COM objects, and the
        Pythonwin environment
        
        This provides the core functionality.
        '''),
    author='Mark Hammond (et al)',
    author_email='mhammond@users.sourceforge.net',
    url='http://sourceforge.net/projects/pywin32/',
    license='PSF',
    cmdclass={
        'build_ext': win32_build_ext,
    },
    ext_modules=list(collect_extensions()),
    packages=find_packages(),
    use_scm_version=True,
    entry_points={
        'console_scripts': [
            'makepy = win32.com.client.makepy:main',
            'verstamp = win32.verstamp:main',
        ],
    })
