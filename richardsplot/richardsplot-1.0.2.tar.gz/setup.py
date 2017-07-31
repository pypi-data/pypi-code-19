from setuptools import setup, find_packages

setup(
name = 'richardsplot', 
version = '1.0.2',
description = 'Matplotlib plotting standards for Gordon Richards\' group',
author = 'Gordon T. Richards',
author_email = 'gtr@physics.drexel.edu',
url = 'https://github.com/gtrichards/richardsplot',
download_url = 'https://github.com/gtrichards/richardsplot/archive/1.0.tar.gz',
license = 'MIT',
packages=find_packages(exclude=['contrib','docs','tests']),
py_modules=['richardsplot'],
install_requires = ['palettable>=3.0.0','matplotlib>=1.5.1'],
classifiers = [
    'Development Status :: 5 - Production/Stable',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
                ],
keywords = 'richards matplotlib',
    )
