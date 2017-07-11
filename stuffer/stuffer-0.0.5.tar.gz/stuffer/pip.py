from stuffer.core import Action
from stuffer import apt



class Install(Action):
    """Install a package with pip install."""

    def __init__(self, package, upgrade=False, bootstrap=True):
        self.package = package
        self.upgrade = upgrade
        self.bootstrap = bootstrap
        super(Install, self).__init__()

    def prerequisites(self):
        return [
            apt.Install(["python3"], update=False),
            apt.Install(["python3-pip"], update=False),
            Install('pip', upgrade=True, bootstrap=False)
        ] if self.bootstrap else []

    def command(self):
        return "pip3 install {}{}".format("--upgrade " if self.upgrade else "", self.package)
