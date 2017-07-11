import subprocess


def supplier(contents):
    return contents if callable(contents) else lambda: contents


class OutputOf(object):
    def __init__(self, command, shell=False):
        self.command = command
        self.shell = shell
        super(OutputOf, self).__init__()

    def __call__(self):
        return subprocess.check_output(self.command, shell=self.shell).decode()
