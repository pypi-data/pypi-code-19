#!/Anaconda3/python
# storytime

'''
description
'''

from .meta import prepare_object

#----------------------------------------------------------------------#
from .time import GameTime
from .universe import Spacetime
from .universe import Universe
from .universe import PhysicalLaws
from .history import History

class Engine :
    def __init__( self
                , start_time
                , universe: Universe = None
                , physics: PhysicalLaws = None
                , history: History = None
                ):

        self._spacetime = Spacetime( start_time, prepare_object( universe, Universe ) )
        self._physics = prepare_object( physics, PhysicalLaws )
        self._history = prepare_object( history, History )

    def initialize( self, gametime ) :
        (now_time, universe) = self._spacetime.now
        universe.create( now_time, gametime, self._physics )
        # initialize history


    def tick( self, next_time ) :
        self._spacetime.tick( next_time )

    def universe( self, gametime: GameTime ) :
        return self._spacetime.universe( gametime )

    @property
    def now( self ) -> (GameTime, Universe) :
        return self._spacetime.now

    def save( self ):
        raise NotImplementedError

    def load( self, filename ):
        raise NotImplementedError


#----------------------------------------------------------------------#

def raise_sys_exit( ) :
    """Called inside interactive console to return to player_function"""
    raise SystemExit
extra_locals = { "exit" : raise_sys_exit }  # other locals go in here

import code
def interactive_interpreter( local_vars:dict ) :
    """Enter the interactive interpreter"""

    local_vars.update(extra_locals)
    try :
        code.interact( local=local_vars )
    except SystemExit :
        pass

#####################
def player_controller( engine:Engine ) :
    """create a callback to allow step-wise interaction with the simulation"""

    def player_event( gametime: GameTime, command:str ):
        """execute a command from the interactive player"""

        (now_time, universe) = engine.now

        if command == "q" : # quit
            raise StopIteration

        elif command == "c" : # show terrain
            print( "Create:", gametime, now_time, universe  )
            print( engine.initialize( gametime ) )

        elif command == "t": # show terrain
            print( "Terrain: " )
            print( universe.__dprint__ )

        elif command == "e" : # show entities
            print( "Entities: ")
            for entity in universe.entities :
                print(entity)

        elif command == "~": # launch REPL
            interactive_interpreter( locals() )

        else:
            print( "Invalid Command." )
            print( "   - advance turn" )
            print( "c  - create" )
            print( "t  - show terrain" )
            print( "e  - show entities" )

            print( "~  - interactive interpreter; exit() to return, quit() to crash" )
            print( "q  - quit" )

    ###
    return player_event


#----------------------------------------------------------------------#

def tick_controller( engine:Engine ) :
    """create a callback to control the simulation"""
    if not isinstance(engine, Engine):
        raise TypeError("engine is not of type Engine: " + str(type(engine)) )

    def tick_event( gametime ) :
        """advance the game from now_time to gametime"""
        engine.tick(gametime)

    ###
    return tick_event


#----------------------------------------------------------------------#

# ToDo: Fix skipping of the first turn

def loop_fixed( gametime, end_time, tick_event ) :

    stop_iteration = False
    while not stop_iteration :
        if gametime == end_time :
            stop_iteration = True

        ### tick event
        else :
            print( "--- TURN: ", gametime )
            tick_event( gametime )
            gametime = next( gametime )

            # time.sleep(1)


def loop_interactive( gametime, tick_event, player_event ) :
    try:
        while True :
            print( "--- TURN: ", gametime )
            player_input = input( "> " )

            ### player event
            if player_input != "" :
                player_event( gametime, player_input )

            ### tick event
            else :
                tick_event( gametime )
                gametime = next( gametime )
            print( "" )
    except StopIteration:
        print("")



#----------------------------------------------------------------------#
