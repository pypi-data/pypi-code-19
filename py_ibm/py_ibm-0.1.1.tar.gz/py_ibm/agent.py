import numpy as np
from math import floor,atan2,degrees,sin,cos,radians, isnan
from operator import methodcaller

class Agent(object):
    """ Agents that populate a 'world'


    Args:
        position (tuple): (x,y) coordinates pair where agent will be created.
        world (world object): world where agent lives
        active (bool): True if agent is to be created as active.


    Attributes:
        ID (int): next serial number available.
        Instances (dict): dictionary where keys are agent ids and values are the agent Instances themselves.

        position (tuple): (x,y) coordinates pair of agent's current position.
        world (world object): world where agent lives
        active (bool): True if agent is to be created as active.
        id (int): agent's serial number.
    """


    ID=0
    Instances={}

    @classmethod
    def IncrementID(self):
        self.ID+=1

    @classmethod
    def ActiveAgents(self):
        """
        Returns:
        (list): containing the id of all active agents.
        """
        return [ag.id for ag in self.Instances.values() if ag.active == True]



    def __init__(self, position, world,active=True, id=None):
        self.world = world
        self.position = self.world.topology.in_bounds(position)
        self.active=active
        #self.IncrementID()
        if id==None:
            self.id=self.ID
        else:
            self.id=id
        self.Instances[self.id]=self
