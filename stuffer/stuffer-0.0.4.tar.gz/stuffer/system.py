import getpass
import os

from stuffer.core import Action


class ShellCommand(Action):
    def __init__(self, command):
        self._command = command
        super().__init__()

    def command(self):
        return self._command

    def use_shell(self):
        return True


def real_user():
    return os.environ.get('SUDO_USER', getpass.getuser())

