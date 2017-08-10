"""
Lore Environment

Key attributes and paths for this project
"""
import os
import sys
import glob


TEST = 'test'
DEVELOPMENT = 'development'
PRODUCTION = 'production'


# Load environment variables from disk
for var in glob.glob("/conf/env/*"):
    if os.path.isfile(var):
        os.environ[os.path.basename(var)] = open(var).read()

env_file = '.env'
if os.path.isfile(env_file):
    from dotenv import load_dotenv
    load_dotenv(env_file)

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    default_name = TEST
else:
    default_name = DEVELOPMENT

name = os.environ.get('LORE_ENV', default_name)
root = os.getcwd()
project = os.environ.get('LORE_PROJECT', root.split(os.sep)[-1])
sys.path = [root] + sys.path
work_dir = 'tests' if name == TEST else os.environ.get('WORK_DIR', root)
models_dir = os.path.join(work_dir, 'models')
data_dir = os.path.join(work_dir, 'data')
tests_dir = os.path.join(root, 'tests')
version_path = '.python-version'
pyenv = os.path.join(os.environ['HOME'], '.pyenv')
bin_pyenv = os.path.join(pyenv, 'bin', 'pyenv')
if not os.path.exists(bin_pyenv):
    bin_pyenv = None

python_version = None
prefix = None
bin_python = None
bin_pip = None
bin_lore = None


def set_python_version(version=None):
    """Set the python version for this lore project, to establish the location
    of key binaries.
    
    :param version:
    :type version: str
    """
    global python_version
    global prefix
    global bin_python
    global bin_pip
    global bin_lore
    
    if not version:
        if os.path.exists(version_path):
            with open(version_path, 'r') as f:
                version = f.read().strip()

    python_version = version
    if python_version:
        prefix = os.path.join(
            os.environ['HOME'],
            '.pyenv',
            'versions',
            python_version,
            'envs',
            project
        )
        bin_python = os.path.join(prefix, 'bin', 'python')
        bin_pip = os.path.join(prefix, 'bin', 'pip')
        bin_lore = os.path.join(prefix, 'bin', 'lore')

set_python_version()


def exists():
    """Test whether the current working directory has a valid lore environment.
    
    :return:  bool True if the environment is valid
    """
    return python_version is not None
