"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-chronograph-ispm-new',
    version='0.3.5',
    description='Django Chronograph ISPM customized by mportela',
    long_description=long_description,
    author='ISPM',
    author_email='dev@ispm.com',
    license='BSD',
    keywords='cron django-chronograph',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    url='https://github.com/ISPM/ispm-django-chronograph',
    classifiers = [
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe = False,
    extras_require = {
        'Django': ['Django>=1.5'],
        'DateUtil': ['python-dateutil<=1.5']
    },
    dependency_links = ['http://labix.org/download/python-dateutil/python-dateutil-1.5.tar.gz'],
    package_data = {
        '': ['docs/*.txt', 'docs/*.py'],
        'chronograph': ['templates/*.*', 'templates/*/*.*', 'templates/*/*/*.*', 'fixtures/*'],
    },
    scripts = ['bin/chronograph'],
)
