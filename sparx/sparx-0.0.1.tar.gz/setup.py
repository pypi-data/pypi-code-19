import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requires = [
    "python-dateutil",
    "pandas",
    "geopy",
    "scipy",
    "numpy",
    "scikit-learn",
    "blaze"
]

with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name = "sparx",
    version = "0.0.1",
    description = "Sparx is a simplified data munging, wrangling and preparation library",
    long_description = LONG_DESCRIPTION,
    url = 'http://sparx.cleverinsight.co',
    license = 'BSD',
    author = 'Bastin Robins J',
    author_email = 'robin@cleverinsight.co',
    packages = find_packages(exclude=['tests']),
    download_url = '',
    include_package_data = True,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        "Natural Language :: English",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ],
    install_requires = requires,
    tests_require = [],
    keywords='sparx data-science data-analysis data-preprocessing data-wrangling data-cleaning',
)
