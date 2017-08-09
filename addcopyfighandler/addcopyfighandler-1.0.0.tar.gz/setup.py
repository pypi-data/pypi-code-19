from setuptools import setup

with open('README.rst') as readme:
    long_description = readme.read()

import addcopyfighandler

setup(
    name = "addcopyfighandler",
    version = '%i.%i.%i' % addcopyfighandler.__version__,

    py_modules=["addcopyfighandler"],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],

    # metadata for upload to PyPI
    author = "Josh Burnett",
    author_email = "github@burnettsonline.org",
    description = "Adds a Ctrl+C handler to matplotlib figures for copying the figure to the clipboard",
    long_description=long_description,
    license = "MIT",
    keywords = "addcopyfighandler figure matplotlib handler copy",
    url = "https://github.com/joshburnett/addcopyfighandler",
)