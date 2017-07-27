from fas.commands.functions import Functions
from fas.commands.spots import Spots
from fas.commands.executions import Executions
from fas.commands.profiles import Profiles


class Faaspot(object):

    def __init__(self):
        self.functions = Functions()
        self.spots = Spots()
        self.executions = Executions()
        self.profiles = Profiles()
