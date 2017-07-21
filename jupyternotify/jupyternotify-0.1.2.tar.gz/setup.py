# -*- coding: utf-8 -*-

import os
from setuptools import find_packages, setup


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    readme = f.read()

with open('LICENSE.txt') as f:
    license = f.read()

setup(
    name='jupyternotify',
    version='0.1.2',
    description='A Jupyter Notebook %%magic for Browser Notifications of Cell Completion',
    long_description=readme,
    author='Michelangelo D\'Agostino',
    author_email='mdagostino@shoprunner.com',
    url='https://github.com/shoprunner/jupyter-notify',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    package_data={'jupyternotify': ['js/*.js']},
    install_requires=[
        'ipython',
        'jupyter'
    ]
)
