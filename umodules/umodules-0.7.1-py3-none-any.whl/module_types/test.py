
from umodules.module_type import IModuleType


class TestModuleType(IModuleType):

    def __init__(self):
        super().__init__()
        self.name = 'test'

    def install(self, project):
        super().install(project)

    def activate(self):
        super().activate()

