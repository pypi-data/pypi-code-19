from setuptools import setup
from codecs import open
from os import path

from sphinxcontrib.swaggersphinx import __version__

root_dir = path.abspath(path.dirname(__file__))

with open(path.join(root_dir, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='sphinxcontrib-swaggersphinx',
    version=__version__,

    description='Convert swagger JSON files to tables in Sphinx',
    long_description=long_description,

    url='https://github.com/timster/sphinxcontrib-swaggersphinx',

    author='Tim Shaffer',
    author_email='timshaffer@me.com',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Database :: Front-Ends',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='sphinx swagger documentation',

    packages=['sphinxcontrib', 'sphinxcontrib.swaggersphinx'],
)