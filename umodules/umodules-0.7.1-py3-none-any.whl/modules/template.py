
from umodules.module_type import IModuleType


class Template(IModuleType):

    def __init__(self):
        self.name = 'template'

    def install(self, project):
        super().install(project)

    def init(self):
        super().init()
