from setuptools import setup
from codecs import open
from os import path

from mpls import __version__

here = path.abspath(path.dirname(__file__))


def readme():
    with open(path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()


setup(
    name='mpls',
    version=__version__,
    description='An open library of matplotlib styles',
    long_description=readme(),

    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],

    keywords='plotting matplotlib styles',
    url='https://github.com/scruffy-t/mpls',
    download_url='https://github.com/scruffy-t/mpls/archive/{}.tar.gz'.format(__version__),
    author='Tobias Schruff',
    author_email='tobias.schruff@gmail.com',
    license='BSD (3-clause)',
    packages=['mpls'],
    install_requires=['matplotlib'],
    zip_safe=False
)
