import sys
import os
from shutil import copyfile

from setuptools import setup, find_packages, __version__

import sovrin_client_rest

v = sys.version_info
if sys.version_info < (3, 5):
    msg = "FAIL: Requires Python 3.5 or later, " \
          "but setup.py was run using {}.{}.{}"
    v = sys.version_info
    print(msg.format(v.major, v.minor, v.micro))
    print("NOTE: Installation failed. Run setup.py using python3")
    sys.exit(1)

# Change to ioflo's source directory prior to running any command
try:
    SETUP_DIRNAME = os.path.dirname(__file__)
except NameError:
    # We're probably being frozen, and __file__ triggered this NameError
    # Work around this
    SETUP_DIRNAME = os.path.dirname(sys.argv[0])

if SETUP_DIRNAME != '':
    os.chdir(SETUP_DIRNAME)

SETUP_DIRNAME = os.path.abspath(SETUP_DIRNAME)

METADATA = os.path.join(SETUP_DIRNAME, 'sovrin_client_rest', '__metadata__.py')
# Load the metadata using exec() so we don't trigger an import of ioflo.__init__
exec(compile(open(METADATA).read(), METADATA, 'exec'))


setup(
    name='ledger-rest-api-dev',
    version=__version__,
    description='REST wrapper for Sovrin client',
    long_description='REST wrapper for Sovrin client',
    url='https://github.com/evernym/sovrin-client-rest',
    author=__author__,
    author_email='dev@evernym.us',
    license=__license__,
    keywords='Sovrin Client REST',
    packages=find_packages(exclude=['test', 'test.*',
                                    'docs', 'docs*']),
    package_data={
        '':       ['*.txt',  '*.md', '*.rst', '*.json', '*.conf', '*.html',
                   '*.css', '*.ico', '*.png', 'LICENSE', 'LEGAL']},
    install_requires=['aiohttp', 'requests', 'psutil', 'indy-node==1.0.28'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest']
)


CONFIG_DIR = os.path.dirname(sovrin_client_rest.__file__)
CONFIG_FILE = os.path.join(CONFIG_DIR, "sovrin_client_rest_config.py")

if not os.path.exists(CONFIG_FILE):
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    copyfile('sovrin_client_rest/config_example.py', CONFIG_FILE)
