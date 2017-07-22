from fas.commands.deployments import Deployments
from fas.commands.spots import Spots
from fas.commands.executions import Executions
from fas.commands.profiles import Profiles


class Faaspot(object):

    def __init__(self):
        self.deployments = Deployments()
        self.spots = Spots()
        self.executions = Executions()
        self.profiles = Profiles()
