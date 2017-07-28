
import dotmap

from abc import ABCMeta, abstractmethod
from yapsy.IPlugin import IPlugin


class IModuleType(IPlugin):

    __metaclass__ = ABCMeta

    def __init__(self):
        self._name = "none"

    @property
    def name(self):
        """Set and Returns the Name of this Module"""
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @abstractmethod
    def install(self, project):
        pass

    '''
        Return a Status of the current Module

        0 - Up To Date
        1 - Modified
    '''
    @abstractmethod
    def status(self, project, module):
        ret = dotmap.DotMap()
        ret.status = 0
        ret.message = 'is Not Supported'
        return ret

    @abstractmethod
    def pull(self, project, module):
        pass
