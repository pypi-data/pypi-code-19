# Created by queenie luc on 01/04/2017
try:
    from setuptools import find_packages
    from distutils.core import setup
except ImportError:
    from distutils.core import setup

__VERSION__ = {}
execfile('cypress_common/version.py', __VERSION__)

try:
    # for local package distribution build
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()
except IOError:
    # for package install
    with open('cypress_common.egg-info/requires.txt') as f:
        requirements = f.read().splitlines()

config = {
    'description': 'Istuary DeepVision Cypress Common Library',
    'author': 'Istuary DeepVision Team (Cypress)',
    'author_email': "cypress-dev@istuary.com",
    'url': 'https://www.istuary.com',
    'version': __VERSION__['VERSION'],
    'install_requires': requirements,
    'packages': find_packages(exclude=['docker', 'tests']),
    'package_dir': {'cypress_common': 'cypress_common'},
    'scripts': [],
    'license': 'MIT',
    'name': 'cypress_common'
}

setup(**config)
