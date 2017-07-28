
import os
import logging
import dotmap
import umodules.helper as helper

from umodules.module_type import IModuleType
from urllib.parse import urlparse


def _run(project, module):
    """Pull a Module from a Local Source.

    Local Modules are 'usually' relative to the Main Project

    :param project:
    :param module:
    """
    src = os.path.abspath(urlparse('{0}/{1}'.format(module.url, module.name)).path)
    dst = os.path.abspath('{0}/{1}/Assets/{2}'.format(project.repository_path, module.name, module.name))


    logging.debug('- checking if repo folder already exists')
    if (os.path.exists(dst)):
        logging.debug('- repo found at {0} . . . cleaning'.format(dst))
        helper.clean_folder(dst)

    logging.debug('- checking if source folder exists')
    if (os.path.exists(src)):
        logging.debug('- source found at {0} . . . copying'.format(dst))
        helper.copy_tree(src, dst)
    else:
        raise Exception('Local Module {0} was Not Found'.format(module.name))


class LocalCopy(IModuleType):

    def __init__(self):
        super().__init__()
        self.name = 'local_copy'

    def install(self, project):
        return super().install(project)

    def status(self, project, module):
        #   set default branch to master
        if 'branch' not in module:
            module.branch = 'master'
        ret = dotmap.DotMap()
        ret.code = 0
        ret.message = "Ignored"
        return ret

    def pull(self, project, module):
        _run(project, module)

