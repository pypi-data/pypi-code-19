#!/Anaconda3/python
# storytime

'''
description
'''

from .time import GameTurn
from .spatial.surfaces import CoordR
from .actors import Actor

from .universe import Planet
from .universe import Universe

from .setting import Season
from .setting import Animal


#----------------------------------------------------------------------#

def sample_universe( size_x=20, size_y=10 ) :
    # define time
    start_time = GameTurn( 0, Season.SUMMER )
    end_time = GameTurn( 10, Season.SUMMER )

    # construct terrain
    planet = Planet( 10 )

    ### initialize Universe container
    universe = Universe( planet )

    ### initial population
    universe.add_entity( Actor( CoordR( [3, 3] ), start_time, features=[Animal.FEMALE] ) )
    universe.add_entity( Actor( CoordR( [7, 7] ), start_time, features=[Animal.MALE] ) )
    universe.add_entity( Actor( CoordR( [2, 2] ), start_time, features=[Animal.MALE, Animal.DEAD] ) )

    return universe


#----------------------------------------------------------------------#

from .engine import Engine


def sample_engine( start_time ) :
    engine = Engine( start_time )



def new_game( start_time, universe ):
    engine = Engine( start_time, universe )

    return engine
