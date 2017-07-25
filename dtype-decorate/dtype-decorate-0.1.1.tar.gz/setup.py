from setuptools import setup, find_packages
import sys

if sys.version_info < (3, 3):
    sys.exit('Python < 3.3 is not supported')


with open('requirements-test.txt') as fs:
    TEST_REQUIREMENTS = fs.read().strip().split('\n')


with open('VERSION') as fs:
    VERSION = fs.read().strip()

with open('classifiers.txt') as fs:
    CLASSIFIERS = fs.read().strip().split('\n')


def readme():
    with open('README.rst') as fs:
        return fs.read()

setup(name='dtype-decorate',
      version=VERSION,
      license='MIT',
      description='data type check and conversion decorators',
      long_description=readme(),
      classifiers=CLASSIFIERS,
      author='Mirko Maelicke',
      author_email='mirko.maelicke@kit.edu',
      test_suite='nose.collector',
      tests_require=TEST_REQUIREMENTS,
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False
)