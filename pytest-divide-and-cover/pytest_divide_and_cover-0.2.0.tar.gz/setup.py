"""A setuptools based setup module."""

# Always prefer setuptools over distutils
from setuptools import setup
# To use a consistent encoding
from codecs import open as c_open
from os import path

HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with c_open(path.join(HERE, 'README.rst'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name='pytest_divide_and_cover',

    version='0.2.0',

    description='Picky test coverage for pytest',
    long_description=LONG_DESCRIPTION,

    # url='https://github.com/mwchase/class-namespaces',

    author='Max Woerner Chase',
    author_email='max.chase@gmail.com',

    license='Apache 2.0',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',

        "Framework :: Pytest",
    ],

    keywords='coverage ',

    py_modules=['pytest_divide_and_cover'],
    package_dir={'': 'src'},

    install_requires=['divide_and_cover', 'pytest'],

    entry_points={
        'pytest11': [
            'divide_and_cover = pytest_divide_and_cover',
        ]
    },
)
