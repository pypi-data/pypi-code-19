#!/usr/bin/env python
from setuptools import setup, find_packages
import codecs

version = '1.3.0'

entry_points = {
}


def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.schema',
    version=version,
    author='Jason Madden',
    author_email='open-source@nextthought.com',
    description=('Zope schema related support'),
    long_description=_read('README.rst'),
    license='Apache',
    keywords='zope schema',
    url='https://github.com/NextThought/nti.schema',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Zope3',
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'Acquisition',
        'nti.i18n',
        'six',
        'setuptools',
        'zope.event',
        'zope.schema',
        'zope.i18n',
        'zope.i18nmessageid',
        'zope.vocabularyregistry',
        'zope.deferredimport',
    ],
    extras_require={
        'test': [
            'pyhamcrest',
            'nti.testing',
            'zope.testrunner',
        ],
    },
    namespace_packages=['nti'],
    entry_points=entry_points,
)
