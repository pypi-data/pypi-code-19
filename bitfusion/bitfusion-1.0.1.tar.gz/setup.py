import os
from setuptools import setup, find_packages

this_dir = os.path.dirname(os.path.realpath(__file__))

# Get the version from VERSION file
version_file = open(os.path.join(this_dir, 'bitfusion', 'VERSION'))
version = version_file.read().strip()
version_file.close()

INSTALL_DEPS = [
  'python-dateutil >= 2.6.0',
  'pytz >= 2016.10',
  'requests >= 2.13.0',
  'requests-toolbelt >= 0.7.1',
]

TEST_DEPS = [
  'mock',
  'pytest',
]

setup(
  name='bitfusion',
  version=version,
  description='Python SDK for developing against the Bitfusion Platform',
  packages=find_packages(),
  package_data={'bitfusion': ['VERSION']},
  author='Brian Schultz',
  author_email='brian@bitfusion.io',
  url='http://www.bitfusion.io',
  install_requires=INSTALL_DEPS,
  tests_require=TEST_DEPS,
  extras_require={'test': TEST_DEPS},
  setup_requires=['pytest-runner'],
)
