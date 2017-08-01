from setuptools import setup

import sys

if sys.version_info < (2,7):
    sys.exit("Sorry Python 2.7 is required for fithic")

setup(
    name = "fithic",
    version = '1.0.1',
    description = 'Hi-C Analysis software created and maintained by the Ay Lab',
    url = 'http://github.com/ay-lab/fithic',
    entry_points = {
        "console_scripts": ['fithic = fithic.fithic:main']
        },
    author = 'Ferhat Ay',
    author_email = 'ferhatay@lji.org',
    license = 'MIT',
    packages = ['fithic'],
    install_requires = [
        'numpy',
        'matplotlib',
        'scipy',
        'scikit-learn[alldeps]',
    ],
    test_suite = "tests",
    zip_safe = False,
  )
