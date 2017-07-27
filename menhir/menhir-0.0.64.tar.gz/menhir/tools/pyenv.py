"""
Pyenv based tool for menhir.

The ``pyenv`` tool provides the ``virtualenv`` target to create a
virtualenv for each of the repository's projects.  The virtualenv is
loaded with all the project's dependencies as specified in
``requirements*.txt``.

The version of python to be used can be specified in the menhir configuration
using the `python-version` key, under the `pyenv` key.

"""
from __future__ import absolute_import

import argparse
import logging
import subprocess

from os import getenv
from os.path import expanduser, isdir, join

from git import Repo
from menhir.tool import Tool
from menhir.tool_utils import (
    FAIL,
    OK,
    package_script,
    tool_env,
    working_dir
)

from menhir.utils import method, multi

log = logging.getLogger(__name__)


def tool():
    return Pyenv()


class Pyenv(Tool):

    def dir_info(tool, path, info):
        from glob import glob
        from os.path import exists, join
        setup_py = join(path, 'setup.py')
        requirements = join(path, 'requirements*.txt')
        files = glob(requirements)
        has_requirements = exists(setup_py) or bool(files)
        return {
            'project_recognised': has_requirements,
            'can_run': has_requirements,
        }

    def dependencies(tool, path):
        return []

    def arg_parser(tool, **kwargs):
        return parser(**kwargs)

    def execute_tool(tool, path, info, args,):
        """Execute a build phase."""
        return task(path, info, args)


def parser(**kwargs):
    parser = argparse.ArgumentParser(
        description="Manage project specific pyenv virtualenvs",
        **kwargs
    )
    parsers = parser.add_subparsers(help="pyenv commands", dest='phase')
    p = parsers.add_parser(
        'virtualenv',
        help='Build a pyenv virtualenv with the projects dependencies'
    )
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    p = parsers.add_parser(
        'install-virtualenv',
        help='Install pyenv-virtualenv (assumes pyenv installed)'
    )
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    p = parsers.add_parser(
        'safety',
        help='Run the safety vulnerability check'
    )
    p.add_argument('remainder', nargs=argparse.REMAINDER)

    return parser


@multi
def task(path, info, args):
    return args.phase


@method(task, 'virtualenv')
def task_virtualenv(path, info, args):
    if (
            'changed' not in info or
            info['changed'].get('self') or
            info['changed'].get('dependents')
    ):
        log.info('Running pyenv requirements in %s', path)

        env = tool_env()

        python_version = info.get('pyenv', {}).get('python-version')
        if python_version:
            env['PYTHON_VERSION'] = python_version

        with package_script("/tools/pyenv/requirements.sh") as f:
            with working_dir(path):
                res = subprocess.call(
                    [f.name, path, info['project-name']],
                    env=env,
                )
                if res:
                    return FAIL
                return OK
    else:
        log.info('not running pyenv requirements in %s', path)
        return OK


PYENV_VENV_URL = 'https://github.com/yyuu/pyenv-virtualenv.git'


@method(task, 'install-virtualenv')
def task_install_virtualenv(path, info, args):
    pyenv_root = getenv('PYENV_ROOT') or expanduser("~/.pyenv")
    dest = join(pyenv_root, "plugins/pyenv-virtualenv")
    if not isdir(dest):
        Repo.clone_from(PYENV_VENV_URL, dest)
        with open(expanduser("~/.bash_profile"), 'a') as f:
            f.write('eval "$(pyenv virtualenv-init -)"\n')
    return OK


@method(task, 'safety')
def task_safety(path, info, args):
    import subprocess
    from menhir.tool_utils import package_script

    with package_script("/tools/pyenv/safety.sh") as f:
        res = subprocess.call([f.name], env=tool_env())
        if res:
            return FAIL
    return OK
