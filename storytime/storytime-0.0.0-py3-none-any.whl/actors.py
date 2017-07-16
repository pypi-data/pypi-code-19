#!/Anaconda3/python
# storytime

'''
description
'''

from copy import deepcopy
from enum import Enum

from .spatial.surfaces import Coord
from .time import GameTurn

from .meta import equality_of
from .meta import prepare_ndarray
from .meta import prepare_object

#----------------------------------------------------------------------#

class Feature( Enum ):
    pass


class __Feature( Feature ):
    NULL        = 0
    DEAD        = 1
    SLEEPING    = 2


#####################

class EntityType( Enum ) :
    NULL        = 0
    TERRAIN     = 1
    WEATHER     = 2

    IDEA        = 3
    SAPIENT     = 4

    ANIMAL      = 5
    PLANT       = 6

    RESOURCE    = 7
    EQUIPMENT   = 8
    STRUCTURE   = 9


#----------------------------------------------------------------------#

class Entity:

    def __init__( self,
                  position:Coord = None,
                  creation_turn:GameTurn = None,
                  features:list = None,
                  index:int = None
                  ):
        self.index = index
        self.creation_turn  = creation_turn

        self.position       = position

        self.features = prepare_object(features, list)


    def __eq__(self,other):
        primary_key = ("index",)
        return equality_of( self, other, primary_key )


    def __str__(self):
        string  = "<Entity "+str( self.index ) + ": "
        string += str(self.position) + " "
        string += str(self.features)
        string += ">"
        return string


    def move(self, destination):
        pass


    def tick(self, population, universe):
        pass


    def finalize(self, population, universe):
        pass


#####################

class Terrain( Entity ) :
    pass


#####################

class Weather( Entity ) :
    pass


#####################

class Idea( Entity ) :
    pass


#####################

class Structure( Entity ) :
    pass


#####################

class Equipment( Entity ) :
    pass


#####################

class Resource( Entity ) :
    pass


#####################

class Plant( Entity ) :
    pass


#####################

class Animal(Entity):
    def reproduce(self, population):
        pass


#####################

class Actor( Animal ):
    pass


#----------------------------------------------------------------------#

#----------------------------------------------------------------------#

class Cluster :
    pass



#----------------------------------------------------------------------#

class Faction :
    pass


#----------------------------------------------------------------------#

class Organization :
    pass


#----------------------------------------------------------------------#

class Civilization :
    pass


#----------------------------------------------------------------------#

class Population :
    def __init__( self, members: list = None ) :

        if members is None :
            self.members = list( )
        else :
            self.members = deepcopy( members )


    def __str__( self ) :
        population_size = len( self.members )
        string = "<Population: " + str( population_size ) + ">"
        return string


    def add( self, member ) :
        self.members.append( member )


    def tick( self, universe ) :
        # make decisions
        for member in self.members( ) :
            member.tick( self, universe )

        # apply decisions
        for member in self.members( ) :
            member.finalize( self, universe )


    def members( self ) :
        for member in self.members( ) :
            yield member
            # raise StopIteration


#####################

class PopulationField:
    pass


#----------------------------------------------------------------------#

class Society :
    pass


#####################

class SocietyField :
    pass


#----------------------------------------------------------------------#
