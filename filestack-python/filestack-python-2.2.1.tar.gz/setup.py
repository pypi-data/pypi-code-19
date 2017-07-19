import os
import re
from pip.req import parse_requirements
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

version = ''
with open('filestack/version.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='filestack-python',
    version=version,
    license='ISC',
    description='Filestack Python SDK',
    # long_description=read('README.md'),
    url='https://github.com/filestack/filestack-python',
    author='filestack',
    author_email='support@filestack.com',
    packages=find_packages(),
    install_requires=[
        'coveralls==1.1',
        'future==0.16.0',
        'httmock==1.2.6',
        'magicmock==0.3',
        'mock==2.0.0',
        'pylint==1.7.1',
        'pytest==3.0.7',
        'pytest-cov==2.5.0',
        'requests==2.13.0',
        'requests-mock==1.3.0',
        'responses==0.5.1',
        'trafaret==0.9.0',
        'unittest2==1.1.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
    ],
)