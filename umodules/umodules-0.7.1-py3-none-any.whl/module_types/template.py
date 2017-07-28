
from umodules.module_type import IModuleType


class Template(IModuleType):

    def __init__(self):
        super().__init__()
        self.name = 'template'

    def install(self, project):
        super().install(project)

    def pull(self, project, module):
        super().run(project, module)

