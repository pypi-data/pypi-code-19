"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path, listdir
from functools import partial
import traceback

here = path.abspath(path.dirname(__file__))

VERSION_FILENAME = 'VERSION'
version = open(path.join(here, "cfboot", VERSION_FILENAME)).read().strip()
long_description = open(path.join(here, "doc", 'README.md')).read()

def sub_script_data_files ( name ):
    sub_dir = path.join(here, "cfboot", "scripts", name)
    return [path.join("scripts", name, fn)
            for fn in listdir(sub_dir)
            if path.isfile(path.join(sub_dir, fn))]

setup(
    name='cf-boot',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=version,

    description="""A declarative mechanism for
    bootstrapping cloudfoundry products""",

    long_description="""The project provides a cleaner alternative
    to long, complex, monolithic,
bootstrap scripts, by decoupling the 'how' and 'what'
    components of bootstrapping.""",

    # The project's main homepage.
    url='https://github.build.ge.com/hubs/cf-bootstrapper',

    # Author details
    author='Ernesto Alfonso, Weijie Lin',
    author_email='ernesto.alfonsogonzalez@ge.com, weijie.lin@ge.com',

    # Choose your license
    license='BSD',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='cloudfoundry cf bootstrap',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    # packages=["cf_bootstrapper"],

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    # py_modules=["cf_bootstrapper"],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    # install_requires=['peppercorn'],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'graph': ['graphviz'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    data_files={
        # 'sample': [],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file'])],

    package_dir={'cfboot': 'cfboot'},
    package_data= {"cfboot": reduce(lambda a, b: a+b, map(sub_script_data_files,  (
        # "postgres-bootstrap",
        # "strip-url-protocol",
        "create-service",
        "create-uaa-clients",
        "extract-service-credentials",
        "create-unique-cf-home",
        "create-acs-policy",
        "cf-push-app",
        "cf-cups",
        "service"
    )))+[VERSION_FILENAME]},

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'cf-boot=cfboot.master.bootstrap:main',
        ],
    },
)
