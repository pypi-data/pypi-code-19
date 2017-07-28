#   Copyright 2016, SpockerDotNet LLC

import git
import logging
import os
import dotmap
import umodules.helper as helper

from umodules.module_type import IModuleType


def _pull(url, repo, branch):
    try:
        logging.debug('- using git to pull {0} from {1}'.format(branch, url))
        git.Repo.clone_from(url, repo, branch=branch, recursive=True)
    except Exception as e:
        raise Exception(e)


def _status(project, module):
    ret = dotmap.DotMap()
    try:
        git_path = _get_path(project, module)
        repo = git.Repo(git_path)
        status = repo.git.status()
        message = "is Unknown"
        code = -1
        if status.find('up-to-date') >= 0:
            message = "is Up To Date"
            logging.debug('- module {0} is up-to-date'.format(module.name))
            code = 0
        if status.find('modified') >= 0:
            message = "has Modified Files"
            logging.debug('- module {0} has modified files'.format(module.name))
            code = 1
        if status.find('untracked') >= 0:
            message = "has Untracked Files"
            logging.debug('- module {0} has untracked files'.format(module.name))
            code = 2
        ret.code = code
        ret.message = message
        return ret
    except Exception as e:
        logging.error('- unable to get status from git')
        raise Exception(e)


def _get_path(project, module):
    path = os.path.abspath('{0}/{1}'.format(project.repository_path, module.name))
    if module.is_main:
        path = os.path.abspath('{0}'.format(project.project_path))
        #   remove existing repo folder
    return path


class ModuleTypeGit(IModuleType):

    def __init__(self):
        super().__init__()
        self.name = 'git'

    def pull(self, project, module):
        super().pull(project, module)
        #   set default branch to master
        if 'branch' not in module:
            module.branch = 'master'
        git_path = _get_path(project, module)
        if os.path.exists(git_path):
            helper.clean_folder(git_path)
        _pull(module.url, git_path, module.branch)

    def status(self, project, module):
        #   set default branch to master
        if 'branch' not in module:
            module.branch = 'master'
        return _status(project, module)

    def install(self, project):
        super().install(project)
