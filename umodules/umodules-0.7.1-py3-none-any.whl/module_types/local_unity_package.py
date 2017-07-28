#   Copyright 2016, SpockerDotNet LLC

import logging
import os
import umodules.helper as helper

from umodules.module_type import IModuleType
from urllib.parse import urlparse

def _pull(project, module):

    src = os.path.abspath(urlparse('{0}/{1}'.format(project.unity_packages_path, module.url)).path)
    dst = os.path.abspath('{0}/{1}'.format(project.repository_path, module.name))
    logging.debug('- importing module to temp project')
    dst = os.path.abspath('{0}/{1}'.format(project.repository_path, module.name))
    helper.import_package(project, src, dst)


class LocalUnityPackage(IModuleType):

    def __init__(self):
        super().__init__()
        self.name = 'local_unity_package'

    def install(self, project):
        super().install(project)

    def status(self, project, module):
        return super().status(project, module)

    def pull(self, project, module):
        super().pull(project, module)
        _pull(project, module)
