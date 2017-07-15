from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='naposapi',
    version='0.1',
    description='API for lookup on the NAPOS database',
    long_description=long_description,
    url='https://github.com/squiddy/pynaposapi',
    author='Reiner Gerecke',
    author_email='me@reinergerecke.de',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['tests']),
    install_requires=['requests', 'lxml', 'cssselect'],
    python_requires='>=3',
)
