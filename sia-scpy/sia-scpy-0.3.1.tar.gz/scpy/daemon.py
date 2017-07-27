from collections import namedtuple

class SiaDaemon(object):
    """The daemon is responsible for starting and stopping the modules which make up the rest of Sia. It also provides endpoints for viewing build constants."""
    def __init__(self, scpy):
        self.scpy = scpy

    def stop(self):
        """
        Cleanly shuts down the Sia daemon

        :return: True if action succeeded
        :raises: SiaError if action was unsuccessful
        """
        return self.scpy.get_api('/daemon/stop')

    @property
    def version(self):
        """
        Version of the Sia daemon
        """
        return self.scpy.get_api('/daemon/version')['version']

    @property
    def constants(self):
        """
        Set of constants in use
        """
        constants = self.scpy.get_api('/daemon/constants')
        return namedtuple("Constants",constants.keys())(*constants.values())
