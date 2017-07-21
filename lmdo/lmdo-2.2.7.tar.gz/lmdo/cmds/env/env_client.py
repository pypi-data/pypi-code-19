
from lmdo.cmds.env.env import Env
from lmdo.cmds.commands import Dispatcher, ExportCommand
from lmdo.cmds.client_factory import ClientFactory


class EnvClient(ClientFactory):
    """Init command client"""
    def __init__(self, args):
        self._env = Env()
        self._dispatcher = Dispatcher()
        self._args = args

    def execute(self):
        if self._args.get('env'):
            if self._args.get('export'):
                self._dispatcher.run(ExportCommand(self._env))


