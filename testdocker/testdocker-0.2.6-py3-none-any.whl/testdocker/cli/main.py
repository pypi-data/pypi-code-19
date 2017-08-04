"""
testdocker.cli.main
~~~~~~~~~~~~~~

CLI interface functions for testdocker.

:copyright: (c) 2017 by Joe Black.
:license: Apache2.

"""

import os
import sys
import distutils.dir_util
import pkg_resources


def yes_no_prompt(prompt):
    """Asks a yes/no question, and returns a boolean response."""
    selection = input('{} [y/n]: '.format(prompt))
    return bool(selection.lower() == 'y')


def ensure_dir_exists(path):
    """Creates path if it doesn't already exist."""
    try:
        os.makedirs(path)
    except OSError:
        pass

def copy_template_files():
    """Copies the template files for tests to ./tests/"""
    tests_path = os.path.join('.', 'tests')
    tests_file_path = os.path.join(tests_path, 'tests.py')
    ensure_dir_exists(tests_path)

    if (os.path.isfile(tests_file_path) and
            not yes_no_prompt('{} exists, overwrite?'.format(tests_file_path))):
        return 'init aborted by user'
    print('Copying files:')
    files = distutils.dir_util.copy_tree(
        pkg_resources.resource_filename(__name__, 'template'), './tests'
    )
    return '\n'.join(files)


def print_usage():
    """Prints the usage for the CLI command."""
    print('Usage: testdocker {init}')
    exit(1)


def main():
    """Entrypoint for CLI command: `testdocker`."""
    args = sys.argv[1:]
    if not args:
        print_usage()
    command = args[0]
    if command == 'init':
        print(copy_template_files())
    else:
        print_usage()
    exit(0)
