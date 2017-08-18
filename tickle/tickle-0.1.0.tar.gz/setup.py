#!/usr/bin/python2.7

from setuptools import setup
from setuptools import find_packages

import tickle as main


setup(
    name=main.__name__,
    version=main.__version__,

    description=main.__doc__.split('\n')[1].strip(),
    long_description=main.__doc__.strip(),
    url='https://bitbucket.org/overridelogic/tickle',
    author='OverrideLogic',
    author_email='info@overridelogic.com',
    maintainer='Francis Lacroix',
    maintainer_email='f@overridelogic.com',

    license='MIT',
    platforms=['any'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],

    packages=find_packages(exclude=['tests', 'tests.*']),
    provides=[main.__name__],

    python_requires='>=2.7',
    setup_requires=['flake8>=3.2.1'],
    tests_require=[],
    test_suite='tests',
)
