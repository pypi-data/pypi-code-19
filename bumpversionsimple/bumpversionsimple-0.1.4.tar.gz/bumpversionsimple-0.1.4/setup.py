# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path
import pypandoc
here = path.abspath(path.dirname(__file__))

name = 'bumpversionsimple'

exec(open(path.join(name, 'version.py')).read())
long_description = pypandoc.convert(path.join(here, 'README.md'), 'rst')

with open("README.rst", 'w') as rst:
    rst.write(long_description[0])

setup(
    name=name,
    version=__version__,
    description='Lazily commit the bumped version of a package',
    long_description=long_description,
    url='https://github.com/wdecoster/bumpversion',
    author='Wouter De Coster',
    author_email='decosterwouter@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='package development',
    packages=find_packages(),
    install_requires=[],
    package_data={'bumpversionsimple': []},
    package_dir={'bumpversion': 'bumpversionsimple'},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'bumpversion=bumpversionsimple.bumpversionsimple:main',
        ],
    },
)
