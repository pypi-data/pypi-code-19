#   Copyright 2016, SpockerDotNet LLC

import logging
import os
import umodules.helper as helper

from umodules.module_type import IModuleType


def _pull(project, module):
    src = os.path.abspath('{0}/{1}.unitypackage'.format(project.repository_path, module.name))
    logging.debug('- pulling {0} into {1}'.format(module.url, src))
    file = helper.download_file(module.url, src)
    logging.debug('- downloaded file {0}'.format(file))
    logging.debug('- importing module to temp project')
    dst = os.path.abspath('{0}/{1}'.format(project.repository_path, module.name))
    helper.import_package(project, src, dst)


class RemoteUnityPackage(IModuleType):

    def __init__(self):
        super().__init__()
        self.name = 'remote_unity_package'

    def install(self, project):
        super().install(project)

    def status(self, project, module):
        return super().status(project, module)

    def pull(self, project, module):
        super().pull(project, module)
        _pull(project, module)
