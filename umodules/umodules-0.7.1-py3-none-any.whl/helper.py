#   Copyright 2016, SpockerDotNet LLC

import os
import stat
import shutil
import errno
import platform
import logging
import subprocess
import os
import wget
import dotmap

from distutils.dir_util import copy_tree
from distutils.file_util import copy_file


def import_package(project, src, dest):
    logging.debug('- importing unity package from {0} into {1}'.format(src, dest))
    cmd = '{0} -createProject {1} -importPackage \"{2}\" -quit -batchmode -nographics'\
        .format(build_unity_command(project.unity_path), dest, src)
    #cmd = '{0} -createProject {1} -importPackage \"{2}\" '\
    #    .format(build_unity_command(project.unity_path), dest, src)
    try:
        run_command(cmd)
    except Exception as e:
        logging.error(e)
        raise Exception('Unable to Import Unity Package')


def download_file(url, dest):
    logging.debug('- attempting to download {0}'.format(url))
    try:
        file = wget.download(url, dest)
        return file
    except Exception as e:
        logging.error(e)
        raise Exception('Unable To Download File')


def copy_module(project, module):
    logging.debug('- there are {0} module includes'.format(len(module.includes)))
    for include in module.includes:
        src = os.path.abspath('{0}/{1}/{2}'.format(project.repository_path, module.name, include.dir))
        logging.debug("- checking to see if module source available at [{0}]".format(src))
        if not os.path.exists(src):
            logging.debug('- module source missing at [{0}]'.format(src))
            raise Exception('Module Source was Not Found in the Repository')
        dst = os.path.abspath('{0}/{1}'.format(project.project_path, include.todir))
        logging.debug("- checking to see if module destination [{0}] exists".format(dst))
        if os.path.exists(dst):
            if project.args.force:
                clean_folder(dst)
            else:
                raise Exception(
                    'Module Path Already Exists at [{0}] -- Try Using the --force'.format(project.project_path))
        logging.debug('- copying module files from {0} to {1}'.format(src, dst))
        try:
            copy_tree(src, dst)
        except Exception as e:
            logging.error(e)
            raise Exception('Could Not Copy Module Files')
    for ignore in module.ignores:
        src = os.path.abspath('{0}/{1}'.format(project.project_path, ignore.dir))
        logging.debug('- removing module folder {0}'.format(src))
        shutil.rmtree(src)


def clean_all(project):
    logging.debug('- cleaning all')
    #   check if the project path exists
    if os.path.exists(project.project_path):
        #   get project main status
        plugin = get_plugin(project, project.main)
        #   init return status
        status = dotmap.DotMap()

        #   when using the --force no need for status
        if project.args.force is True:
            status.code = 0
        else:
            status = plugin.status(project, project.main)

        if status.code == 0:
            clean_folder(project.repository_path)
            clean_folder(project.project_path)
        else:
            raise Exception('Cannot Clean Project [{0}] when it {1} or Try Using the --force'.format(project.name, status.message))
    else:
        raise Exception('Project Path [{0}] Does Not Exist'.format(project.project_path))

def clean_module(project, module):
    logging.debug('- cleaning module {0}'.format(module.name))
    repo_path = __get_module_repo_path(project, module)
    logging.debug('- cleaning the repository folder {0}'.format(repo_path))
    clean_folder(repo_path)
    for include in module.includes:
        dst = os.path.abspath('{0}/{1}'.format(project.project_path, include.todir))
        logging.debug('- claning the module folder {0}'.format(dst))
        clean_folder(dst)


def clean_folder(folder):
    logging.debug('- removing folder {0}'.format(folder))
    if os.path.exists(folder):
        shutil.rmtree(folder, ignore_errors=False, onerror=__remove_read_only)
    else:
        logging.warning('- folder {0} does not exist'.format(folder))


def get_plugin(project, module):
    plugin = __get_plugin(project, module)
    if plugin is None:
        raise Exception('Module Type {0} Not Supported'.format(module.type))
    return plugin


def run_command(cmd):

    if platform.system() != 'Windows' and platform.system() != 'Darwin':
        raise Exception('Unable to Run Unity on {0} Platform'.format(platform.system()))

    logging.debug('- trying to run command [{0}]'.format(cmd))

    try:
        proc = subprocess.Popen(cmd, shell=True)
        proc.communicate()
    except Exception as e:
        logging.error(e)
        raise Exception('Could Not Run Unity Command')


def run_background_command(cmd):

    if platform.system() != 'Windows' and platform.system() != 'Darwin':
        raise Exception('Unable to Run Unity on {0} Platform'.format(platform.system()))

    if platform.system() == 'Windows':
        cmd = 'start /B /I \"UMODULES\" {0}'.format(cmd)
        run_command(cmd)

    if platform.system() == 'Darwin':
        cmd = '{0} &'.format(cmd)
        run_command(cmd)


def build_unity_command(path):

    if platform.system() != 'Windows' and platform.system() != 'Darwin':
        raise Exception('Unable to Run Unity on {0} Platform'.format(platform.system()))

    cmd = ""
    path = os.path.abspath(path)

    if platform.system() == 'Windows':
        logging.debug('- running on Windows')
        exe = 'Unity.exe'
        cmd = '"{0}\{1}"'.format(path, exe)

    if platform.system() == 'Darwin':
        logging.debug('- running on Mac')
        exe = 'Unity.app/Contents/MacOS/Unity'
        cmd = '{0}/{1}'.format(path, exe)

    logging.debug('- command build [{0}]'.format(cmd))
    return cmd


def __handle_remove_readonly(func, path, exc):
    logging.info('- removing read only {0}:{1}'.format(path, exc))
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise

def __remove_read_only(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def __get_module_repo_path(project, module):
    path = os.path.abspath('{0}/{1}'.format(project.repository_path, module.name))
    return path


def __get_module_project_path(project, module):
    path = os.path.abspath('{0}/Assets/{1}'.format(project.project_path, module.name))
    return path


def __get_plugin(project, module):
    logging.debug('- module type is [{0}]'.format(module.type))
    plugin = None
    for module_type in project.module_types:
        if module.type == module_type.plugin_object.name:
            logging.debug('- found plugin for module type of [{0}]'.format(module.type))
            plugin = module_type.plugin_object
    return plugin