"""
runcli.runcli
=============
Main module implementing the functionality for ``runcli``.
"""

import logging
import os
import subprocess
import sys


logger = logging.getLogger(__name__)


def get_runfile_path():
    """Return path to the first Runfile in an ancestor of current dir.

    :raises: a RuntimeError if no Runfile can be located.

    :returns: a string giving the path to the closest Runfile in an
    ancestor of the current working directory.
    """
    path = os.getcwd()
    # check back to the root for the nearest Runfile file
    while(path != os.path.dirname(path)):
        runfile_path = os.path.join(path, 'Runfile')
        if os.path.isfile(runfile_path):
            return runfile_path
        path = os.path.dirname(path)

    raise RuntimeError("Failed to locate 'Runfile' file.")


def main(args):
    """Execute args with the Runfile.

    Find the first Runfile in an ancestor directory from the current
    directory, and execute it as a script, passing it ``args``.

    :param str args: the arguments with which to execute the Runfile.

    :returns: None.
    """
    runfile_path = get_runfile_path()
    cmd = '{runfile_path} {args}'.format(
        runfile_path=runfile_path,
        args=args)

    logger.debug("Executing: {cmd}".format(cmd=cmd))
    try:
        subprocess.check_call(cmd, shell=True)
    except(subprocess.CalledProcessError) as e:
        logger.debug(
            '{cmd} raised:'
            '\n{e}'.format(cmd=cmd, e=e))
