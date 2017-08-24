from distutils.core import setup
version = '1.1.2'

description = """
Bowhead is a Python package for determining cell velocity from the wound healing assay. It combines image detection and velocity determination into one workflow in order to analyze time series imaging data. """

url = 'https://gitlab.com/engel/bowhead/repository/archive.tar.gz?ref='

setup(
    name = 'bowhead',
    version = version,
    download_url = url + version,
    description = 'A wound assay detection and analysis package.',
    long_description = description,
    author = 'Mathias Engel',
    author_email = 'engel@lindinglab.org',
    url = 'https://gitlab.com/engel/bowhead',
    license = 'GNU General Public License Version 3',
    classifiers = [
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires ='>=3.5',
    keywords = ['wound', 'detection', 'velocity', 'healing', 'area', 'cells'],
    packages = ['bowhead'],
)
