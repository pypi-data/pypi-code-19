#!/Anaconda3/python
# storytime

"""
description
"""

from enum import Enum
from enum import unique

#----------------------------------------------------------------------#

from .time import Cycle

class Season( Cycle ) :
    WINTER = 1
    SUMMER = 2



class Battle( Cycle ) :
    DEAL = 9
    BET  = 10
    DRAW = 15


#----------------------------------------------------------------------#

from .actors import Feature

class TerrainType( Feature ):
    OCEAN       = 0
    SEA         = 1
    COAST       = 2
    LAKE        = 3

    FLAT        = 4
    HILL        = 5
    HIGHLAND    = 6
    MOUNTAIN    = 7

    CLIFF       = 8
    RIVER       = 9


class Weather( Feature ):
    COLD = 0
    HOT = 1
    SUNNY = 2
    RAIN = 3


class Idea( Feature ) :
    BELIEF = 0


class Sapient( Feature ) :
    DEAD = 0


class Animal( Feature ) :
    DEAD = 0
    FEMALE = 1
    MALE = 2
    SICK = 4


class Plant( Feature ) :
    GRASS = 0
    TREE = 1
    ANNUAL = 2
    PERRENIAL = 3


class Equipment( Feature ) :
    TOOL = 0
    WORN = 1
    CARRIED = 2
    VEHICLE = 3
    FURNITURE = 4


class Resource( Feature ) :
    LABOR = 0

    FOOD = 1
    MEDICINE = 2
    POISON = 3

    WOOD = 4
    STONE = 5
    METAL = 6


class Structure( Feature ) :
    SHELTER = 0


class CharacterStat( Feature ) :
    STRENGTH = 0
    DEXTERITY = 1
    CONSTITUTION = 2
    INTELLIGENCE = 3
    WISDOM = 4
    CHARISMA = 5


#----------------------------------------------------------------------#

from .spatial.graphs import EdgeColorBase

class Reputation( EdgeColorBase ) :
    NULL = 0
    ACTIVE = 1
    INACTIVE = 2

    RELATIVE = 100
    MARRIED = 101
    PARENT = 110
    CHILD = 111
    SIBLING = 112

    FRIEND = 200

    ENEMY = 300

    NEUTRAL = 400


#----------------------------------------------------------------------#

from .history import ThemeHandler

class ThemeStart( ThemeHandler ) :
    """Theme.START"""

    def consequences( self, event, universe ) :
        return event.consequences


#####################

class Theme( Feature ) :
    NULL            = 0                 # No interaction
    START           = ThemeStart        # Simulation beginning

    ###
    BIG_BANG        = 10                # Create universe
    TECTONIC        = 20                # Large-dilate geologic movement

    ##
    PLANTS          = 100               # Apply plants

    ANIMALS         = 150               # Populate Animals

    ###
    INFLUENCE       = 200
    PRESSURE        = 201
    BRIBE           = 202

    ###
    DISCOVERY       = 300

    ###
    INSTITUTION     = 400

    ###
    FACTION         = 500

    ###
    CIVILIZATION    = 600

    ###
    LANGUAGE        = 700

    ###
    CHARACTER       = 1000              # 2 parents, causes Birth
    BIRTH           = 1001              # N children
    DEATH           = 1002              # 1 character

    MOVE            = 1010

    STUDY           = 1020
    WORK            = 1021
    BUIDING         = 1022
    PARTY           = 1023
    MARRIAGE        = 1050

    REPRODUCTION    = 1500

    ###
    END             = 9999              # Simulation end


#----------------------------------------------------------------------#

class Constants :
    TOTAL_ENERGY = 100000
    PLANK = 0.00001
    ENTROPY = 1
    GRAVITY = 1.0
    FINE_STRUCTURE = 10

    SPEED_OF_LIGHT = 1000.0
    SPEED_OF_SOUND = 100.0

    PLOT_FORCE = 2.0
    INITIAL_FORCE = 100.0

    TIME_FRICTION = 10.0
    LAND_FRICTION = 1.0
    OCEAN_FRICTION = 10.0

    TILE_AREA = 100.0
    TILE_VARIATION = 10.0
    TILE_COUPLING = 1.0


#----------------------------------------------------------------------#

