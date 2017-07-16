import io
import os
import re
import sys
from codecs import open
from distutils.text_file import TextFile

from setuptools import find_packages, setup

__author__ = "benjamin.c.yan"

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'simplekit',
    'simplekit.objson'
]

requires = ['six', 'furl', 'requests', 'python-ntlm==1.1.0']

home = os.path.abspath(os.path.dirname(__file__))
missing = object()


def read_description(*files, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = [io.open(name, encoding=encoding).read() for name in files]
    return sep.join(buf)


def read_dependencies(requirements=missing):
    if requirements is None:
        return []
    if requirements is missing:
        requirements = 'requirements.txt'
    if not os.path.isfile(requirements):
        return []
    text = TextFile(requirements, lstrip_ws=True)
    try:
        return text.readlines()
    finally:
        text.close()


def read_version(version_file):
    with open(version_file, 'rb') as fd:
        result = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                           fd.read(), re.MULTILINE)
        return result.group(1) if result else '0.0.1'


setup(
    name='flask_wx',
    version=read_version('flask_wx/__init__.py'),
    description='A simple and brief utility tools framework',
    long_description=read_description('README.md'),
    author='Benjamin Yan',
    author_email='ycs_ctbu_2010@126.com',
    url='https://github.com/by46/flask_wx',
    packages=find_packages(),
    include_package_data=True,
    install_requires=read_dependencies(),
    license='The MIT License',
    zip_safe=False,
    classifiers=(
    ),
)
