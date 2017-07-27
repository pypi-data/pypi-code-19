"""Utilities for use in tools.

"""

import logging
import re
import sys
from contextlib import contextmanager

from menhir.tool import load_tool

log = logging.getLogger(__name__)

OK = {
    'status': 'ok'
}

FAIL = {
    'status': 'fail'
}

NOTHING_TO_DO = {
    'status': 'nothing_to_do'
}

NON_WORD_PATTERN = re.compile(r'\W')


@contextmanager
def package_script(resource_path, resource_package="menhir"):
    """Execute a block of code with the given script from the package.

    Yields a file like object that is the script written onto the filesystem.
    """
    import tempfile
    import pkg_resources
    import stat
    from os import chmod, remove

    script = pkg_resources.resource_string(resource_package, resource_path)
    fname = None
    try:
        with tempfile.NamedTemporaryFile("wb", delete=False) as f:
            fname = f.name
            f.write(script)
        chmod(fname, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
        yield f
    finally:
        remove(fname)


@contextmanager
def working_dir(path):
    """Execute a block of code within the given working dir."""
    import os
    dir = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(dir)


def tool_env():
    """Return the default tool environment dict."""
    import os
    import os.path

    default_pyenv_root = os.path.join(os.getenv("HOME"), ".pyenv")
    env = {
        "PYENV_ROOT": default_pyenv_root,
    }

    env.update(os.environ)

    return env


def call(cmd, *args, **kwargs):
    """Call a subprocess, returning a menhir result."""
    import subprocess
    res = subprocess.call(cmd, *args, **kwargs)
    if res:
        return FAIL
    return OK


def slugify(s, length=None, replace=NON_WORD_PATTERN):
    s = re.sub(replace, "_", s)
    if length:
        s = s[:length]
    return s


@contextmanager
def run_if(cond, phase_name, path):
    if cond:
        log.info(
            'Running %(phase)s in %(path)s',
            {'phase': phase_name, 'path': path}
        )
        yield True
    else:
        yield False
        log.info(
            'Not running %(phase)s in %(path)s',
            {'phase': phase_name, 'path': path}
        )


def call_tool_chain(path, info, remainder):
    result = OK
    while remainder:
        tool_name = remainder.pop(0)
        tool = load_tool(tool_name)

        parser = tool.arg_parser(add_help=False, prog=tool_name)
        tool_args, unknown = parser.parse_known_args(
            remainder,
            # namespace=copy(args)
        )
        log.debug('tool_args %s: %s', tool_name, tool_args)
        if unknown:
            log.debug('unknown argument: %s', unknown)
            parser.print_help()
            sys.exit(0 if remainder == ['-h'] else 1)

        result = tool.execute_tool(path, info, tool_args)

        remainder = getattr(tool_args, 'remainder', None)
        log.debug('remainder after %s: %s', tool_name, remainder)

        if result['status'] != 'ok':
            return result

    return result


def argv_to_dict(arg_names, arg_values):
    """Convert vectors of arg names and arg values to a dict.

    returns `None, Fail` if the vector lengths do not match.
    """
    if len(arg_names) != len(arg_values):
        print(len(arg_names), len(arg_values))
        return None
    else:
        return {k: v for (k, v) in zip(arg_names, arg_values)}
