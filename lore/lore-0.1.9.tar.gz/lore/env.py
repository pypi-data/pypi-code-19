"""
Lore Environment

Key attributes and paths for this project
"""
import glob
import os
import re
import sys

TEST = 'test'
DEVELOPMENT = 'development'
PRODUCTION = 'production'


def read_version(path):
    version = None
    if os.path.exists(path):
        with open(path, 'r') as f:
            version = f.read().decode('utf-8').strip()
    
    if version:
        return re.sub(r'^python-', '', version)
    
    return version


python_version = None
root = os.getcwd()
while True:
    python_version = read_version(os.path.join(root, 'runtime.txt'))
    if python_version:
        break

    python_version = read_version(os.path.join(root, '.python-version'))
    if python_version:
        break

    root = os.path.dirname(root)
    if root == '/':
        break


# Load environment variables from disk
for var in glob.glob('/conf/env/*'):
    if os.path.isfile(var):
        os.environ[os.path.basename(var)] = open(var).read()

env_file = os.path.join(root, '.env')
if os.path.isfile(env_file):
    from dotenv import load_dotenv
    load_dotenv(env_file)

if len(sys.argv) > 1 and sys.argv[1] == 'test':
    default_name = TEST
else:
    default_name = DEVELOPMENT


name = os.environ.get('LORE_ENV', default_name)
project = os.environ.get('LORE_PROJECT', root.split(os.sep)[-1])
sys.path = [root] + sys.path
work_dir = 'tests' if name == TEST else os.environ.get('WORK_DIR', root)
models_dir = os.path.join(work_dir, 'models')
data_dir = os.path.join(work_dir, 'data')
tests_dir = os.path.join(root, 'tests')
pyenv = os.path.join(os.environ['HOME'], '.pyenv')
bin_pyenv = os.path.join(pyenv, 'bin', 'pyenv')
if not os.path.isfile(bin_pyenv):
    bin_pyenv = None

prefix = None
bin_python = None
bin_pip = None
bin_lore = None
requirements = os.path.join(root, 'requirements.txt')
requirements_in = os.path.join(root, 'requirements.in.txt')
requirements_vcs = os.path.join(root, 'requirements.vcs.txt')

def set_python_version(version):
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

set_python_version(python_version)


def exists():
    """Test whether the current working directory has a valid lore environment.
    
    :return:  bool True if the environment is valid
    """
    return python_version is not None


def launched():
    """Test whether the current python environment is the correct lore env.

    :return:  bool True if the environment is launched
    """
    return sys.prefix == prefix
