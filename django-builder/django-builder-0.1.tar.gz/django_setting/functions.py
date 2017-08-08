import re
import shutil
import sys
from subprocess import Popen, PIPE
from .utils import get_subprocess_output


def check_pyenv_installed():
    if not shutil.which('pyenv'):
        print('pyenv must be installed')
        sys.exit()
    if not shutil.which('pyenv-virtualenv'):
        print('pyenv-virtualenv must be installed')
        sys.exit()


def parse_project_name():
    args_length = len(sys.argv)
    if args_length != 2:
        print('Please enter project name')
        sys.exit()
    return sys.argv[1]


def select_python_version():
    p = Popen(['pyenv', 'versions'], stdout=PIPE)
    out, err = p.communicate()
    out2 = re.sub(r' \(set by.*\)', '', out.decode('utf-8').replace('*', ''))
    version_list = [x.strip() for x in out2.split('\n') if x.strip().startswith('3') and '/' not in x]
    if len(version_list) == 1:
        return version_list[0]
    select_string = 'Available python versions:\n'
    for index, version in enumerate(version_list):
        select_string += ' %s. %s\n' % (index + 1, version)
    select_string += 'Select python version (default: %s): ' % version_list[len(version_list) - 1]
    selected_version = input(select_string)
    if not selected_version:
        selected_version = len(version_list)
    return version_list[int(selected_version) - 1]


def get_pyenv_path(python_version, env_name):
    env_list = get_subprocess_output('pyenv virtualenvs').split('\n')

    def get_version_path(m):
        return '{},{}'.format(m.group(1), m.group(2))

    p = re.compile(r'\s*([\w\W]+?)\s\(created from\s([\w\W]+?)\)')
    env_list = [re.sub(p, get_version_path, env).split(',') for env in env_list if env.strip().startswith(python_version) and env_name in env]
    env = env_list[0]
    path = '{}{}'.format(
        env[1],
        env[0].replace(python_version, '')
    )
    return path