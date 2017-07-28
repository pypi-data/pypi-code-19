
from umodules.module_type import IModuleType


class TestModuleType(IModuleType):

    def __init__(self):
        self.name = 'test'

    def install(self, project):
        super().install(project)

    def activate(self):
        super().activate()

