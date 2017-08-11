import os
import re
from pip.req import parse_requirements
from setuptools import setup, find_packages


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

with open('fs_cli/version.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='filestack-cli',
    version=version,
    license='ISC',
    description='Filestack Command-Line Client',
    url='https://github.com/filestack/filestack-cli',
    author='filestack',
    author_email='support@filestack.com',
    packages=find_packages(),
    install_requires=[
        'click==6.7',
        'filestack-python==2.2.1',
        'requests==2.13.0'
    ],
    entry_points={
        'console_scripts': ['fs-cli=fs_cli.router:cli']
    },
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
