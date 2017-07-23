#!/usr/bin/env python

from setuptools import setup

version = __import__('cairomovie').__version__

setup(
    name='cairomovie',
    packages=[
        'cairomovie'
        ],

    version=version,
    description='Creating a movie with cairo frames.',
    author='Ian Millington',
    author_email='idmillington@googlemail.com',

    url='http://github.com/idmillington/cairomovie',
    download_url='https://github.com/idmillington/cairomovie/tarball/master',

    keywords=['cairomovie', 'cairo', 'pymovie'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Graphics",
        ],

    zip_safe=False,

    # Testing and documentation requirements can be installed with:
    # pip install -r dev-requirements.txt
    install_requires=['moviepy', 'numpy', 'cairocffi']
    )
