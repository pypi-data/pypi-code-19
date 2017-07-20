from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
# To use a consistent encoding
from codecs import open
from os import path
import sys
import shlex

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        if isinstance(self.pytest_args, str):
            self.pytest_args = shlex.split(self.pytest_args)
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

version = '0.0.12'
setup(
    name='mattoolkit',
    version=version,
    description='Material Toolkit cli and library',
    long_description=long_description,
    url='https://gitlab.aves.io/mattoolkit/mattoolkit-client',
    author='Chris Ostrouchov',
    author_email='chris.ostrouchov+mtk-cli@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    cmdclass = {'test': PyTest},
    keywords='material toolkit material science hpc vasp',
    download_url = 'https://gitlab.aves.io/mattoolkit/mattoolkit-client/repository/archive.zip?ref=v%s' % version,
    packages=find_packages(exclude=['docs', 'tests']),
    install_requires=[
        'click',
        'beautifulsoup4',
        'requests',
        'pymatgen',
        'custodian'
    ],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'mtk-cli=mattoolkit.__main__:main'
        ]
    }
)
