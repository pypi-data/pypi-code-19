# -*- coding: utf-8 -*-
"""
.. module:: TODO
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann aljosha.friemann@gmail.com

----------------------------------------------------------------------------
"THE BEER-WARE LICENSE" (Revision 42):
<aljosha.friemann@gmail.com> wrote this file.  As long as you retain this
notice you can do whatever you want with this stuff. If we meet some day,
and you think this stuff is worth it, you can buy me a beer in return.
----------------------------------------------------------------------------

"""

import os, logging, stat, subprocess

from simple_tools.lists import find

from scriptler import sources

logger = logging.getLogger(__name__)

class FailedCommandException(RuntimeError):
    def __str__(self):
        return "Failed to execute command: {}".format(', '.join(self.args))

def get_all(path, only_executable = True):
    for root,dirs,files in os.walk(path):
        for file in files:
            abspath = os.path.join(root, file)

            if only_executable:
                if os.access(abspath, os.X_OK):
                    yield abspath
            else:
                yield abspath

def get_unmanaged(path, managed_scripts):
    for script in get_all(path, False):
        if not find(lambda s: s.name == os.path.basename(script), managed_scripts):
            yield script

def get_managed(path, managed_scripts):
    for script in get_all(path, False):
        if find(lambda s: s.name == os.path.basename(script), managed_scripts):
            yield script

def get_installed(path, managed_scripts):
    managed_script_names = managed_scripts.keys()
    for script in get_all(path):
        name = os.path.basename(script)
        if name in managed_script_names:
            yield name

def make_executable(path):
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)

def execute_command(file_path, command):
    return subprocess.Popen(command.format(file_path), shell=True).wait()

def install(name, script, source, script_dir):
    logger.debug('installing %s to %s', script, script_dir)

    try:
        os.makedirs(script_dir)
    except OSError as e:
        if e.errno != 17:
            raise e

    basepath = os.path.join(script_dir, name)

    sources.get(script.path, source, basepath)

    make_executable(basepath)

    if script.command:
        if execute_command(basepath, script.command) != 0:
            raise FailedCommandException(script.command)

def remove(path):
    logger.debug('deleting %s', path)

    os.remove(path)

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
