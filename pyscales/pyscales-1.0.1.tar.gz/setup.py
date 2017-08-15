import os
from codecs import open
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyscales',
    version='1.0.1',
    description='Simple arithmetic on musical notes',
    long_description=long_description,
    url='https://bitbucket.org/talljosh/pyscales',
    author='J. D. Bartlett',
    author_email='josh@bartletts.id.au',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='music scales notes midi',
    py_modules=['pyscales'],
    install_requires=[],
)
