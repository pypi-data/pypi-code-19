
import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-ws4ever',
    version='0.1.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=1.10',
        'gevent==1.2.1',
        'gevent-websocket==0.10.1',
        'django-ipware>=1.1.6',
        'django-memoize>=2.1.0',
        'voluptuous>=0.8.11',
        'redis>=2.10.5',
        'ujson>=1.35',
    ],
    license='BSD License',
    description='websocket server for django',
    long_description=README,
    author='turen',
    author_email='nb@turen.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
