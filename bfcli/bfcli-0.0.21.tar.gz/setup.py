import os
from setuptools import setup, find_packages

this_dir = os.path.dirname(os.path.realpath(__file__))

# Get the version from VERSION file
version_file = open(os.path.join(this_dir, 'bfcli', 'VERSION'))
version = version_file.read().strip()
version_file.close()

# Get the cli command from COMMAND file
command_file = open(os.path.join(this_dir, 'bfcli', 'COMMAND'))
command = command_file.read().strip()
command_file.close()

setup(
  name='bfcli',
  version=version,
  description='CLI for interactive with the Bitfusion Platform',
  packages=find_packages(),
  package_data={'bfcli': ['VERSION', 'COMMAND']},
  author="Brian Schultz",
  author_email='brian@bitfusion.io',
  url='http://www.bitfusion.io',
  py_modules=['bfcli'],
  install_requires=[
    'analytics-python',
    'bitfusion',
    'click',
    'jsonschema',
    'pyjwt',
    'python-dateutil',
    'pytz',
    'pyyaml',
    'requests',
    'terminaltables',
  ],
  setup_requires=['pytest-runner'],
  tests_require=[
    'pytest',
    'docker',
  ],
  entry_points='''
    [console_scripts]
    {}=bfcli.cli:cli
  '''.format(command),
)
