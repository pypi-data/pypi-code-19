#!/Anaconda3/python
# storytime

"""
description
"""


from enum import Enum
from enum import unique

from copy import deepcopy

from .meta import equality_of


#----------------------------------------------------------------------#
# Time data types

class Cycle( Enum ) :
    """Base class for cyclic enumerations"""

    @classmethod
    def from_index( cls, index ) :
        phase = cls.members( )[index % len( cls )]
        # print("CYCLE INDEX", phase)
        return phase

    @classmethod
    def members( cls ) -> list :
        # __members__ is an ordered dict
        members = list( cls.__members__.values( ) )
        return members


    #####################
    @classmethod
    def first( cls ) -> Enum :
        first_phase = cls.members()[0]
        return first_phase

    @property
    def is_first( self ) -> bool :
        first_phase = type( self ).first( )
        return self == first_phase

    @classmethod
    def last( cls ) -> Enum :
        last_phase = cls.members()[-1]
        return last_phase

    @property
    def is_last( self ) -> bool :
        last_phase = type( self ).last( )
        return self == last_phase


    #####################
    @classmethod
    def __len__( cls ) -> int :
        length = len( cls.members() )
        return length

    @classmethod
    def cycle_duration( cls ) -> int :
        length = cls.last().value
        return length

    @property
    def duration( self ) -> int :
        """member's value minus previous value"""

        duration = 0
        if self == self.members()[0]:
            duration    = self.members()[0].value
        else:
            index       = self.members().index(self)
            duration    = self.members()[index].value - self.members()[index - 1].value
        # print("DURATION", duration, self)
        return duration


    #####################
    def __next__(self):
        for member in self.members() :
            if member.value > self.value:
                return type(self)(member.value)
        return self.first()


#####################

@unique
class __Season( Cycle ) :
    SUMMER = 1
    WINTER = 2


@unique
class __Battle( Cycle ) :
    DEAL = 9
    BET  = 10
    DRAW = 15


#----------------------------------------------------------------------#

class GameTime :
    def __init__( self, tick:int=0 ) :
        self._tick = tick
        self.stop_iteration = False

    @property
    def tick( self ) :
        return self._tick

    def __eq__(self, other):
        primary_key = ("tick",)
        return equality_of( self, other, primary_key )

    def __hash__(self):
        return hash(self._tick)

    def __add__( self ) :
        pass

    def __sub__( self, other ) :
        pass

    def __iter__( self ) :
        return self

    def __next__( self ) :
        if self.stop_iteration is True :
            raise StopIteration

        self._tick += 1
        return str( self )

    def stop( self ) :
        self.stop_iteration = True




#----------------------------------------------------------------------#
import inspect

class GameTurn( GameTime ) :
    """
    GameTurn( )             - 1 turn = 1 turn, no phases
    GameTurn( turn )        - begin on given turn, no phases
    GameTurn( phase )       - 1 turn == 1 phase
    GameTurn( turn, phase ) - begin on given turn and phase
    """

    # ToDo: Eras

    def __init__( self, arg1=None, arg2=None) :
        super().__init__()

        ### empty
        if arg2 is None:
            if arg1 is None:
                self._turn=1
                self._phase=None

            ### ( phase )
            elif isinstance(arg1, Enum):
                self._turn   = 1
                self._phase  = arg1
                if self._turn > 1 or not self._phase.is_first :
                    # print( "IS_FIRST", self._phase, self._phase.is_first )
                    self._tick += self._phase.value - self._phase.first().value

            ### ( phase_cls )
            elif inspect.isclass(arg1) and issubclass( arg1, Cycle ) :
                self._turn = 1
                self._phase = arg1.first()
                if self._turn > 1 or not self._phase.is_first :
                    # print( "IS_FIRST", self._phase, self._phase.is_first )
                    self._tick += self._phase.value - self._phase.first( ).value

            ### ( turn )
            else:
                if arg1 < 0:
                    raise ValueError("GameTurn must be positive: " + str(arg1))
                self._turn = arg1
                self._phase = None
                self._tick += self._turn

        ### ( turn, phase )
        else:

            if arg1 < 0 :
                raise ValueError( "GameTurn must be positive: " + str( arg1 ) )
            self._turn = arg1

            if not isinstance(arg2, Cycle):
                raise TypeError( "arg2 must have type 'Cycle': " + str(type(arg1)) + " " + str(arg1))
            self._phase = arg2

            # duration is applied to tick after the phase is complete, so the first turn has 0 tick
            if self._turn > 1 or not self._phase.is_first:
                self._tick += (self._turn-1) * self._phase.cycle_duration() # contribution from turn
                self._tick += self._phase.value - self._phase.duration  # contribution from phase

            # print( "IS_FIRST", self._phase, self._phase.is_first )


    #####################
    @classmethod
    def from_index( cls, index:int, phase_cls=None ) :
        """Construct GameTurn by inferring turn, phase from an iteration index: count of phases"""

        gameturn = None
        ### empty
        if phase_cls is None:
            gameturn=cls(index)

        ### ( Cycle )
        if issubclass(phase_cls, Cycle):
            turn = index // len( phase_cls ) + 1
            phase = phase_cls.from_index(index)
            # print("turn/phase", turn, phase)
            gameturn = cls(turn, phase)

        else:
            raise TypeError("phase_cls must be subclass of Cycle, or None: "
                            + str( type(phase_cls) ) + " " + str(phase_cls) )

        # print( "TURN INDEX", gameturn )
        return gameturn

    @property
    def turn( self ) :
        return self._turn

    @property
    def phase( self ) :
        return self._phase

    #####################

    def __gt__( self, other ) :
        return self._tick.__gt__( other.tick )

    def __ge__( self, other ) :
        return self._tick.__ge__( other.tick )

    def __lt__( self, other ) :
        return self._tick.__lt__( other.tick )

    def __le__( self, other ) :
        return self._tick.__le__( other.tick )

    def __eq__( self, other ) :
        if not hasattr( other, "_turn" ) or not hasattr( other, "_phase" ):
            raise TypeError("Comparing GameTurn to " + str(type(other)) + " " + str(other) )
        if self._phase is None or other.phase is None:
            if self._phase is not None or other.phase is not None :
                raise TypeError("Phase only set on one side: " + str(self) +", "+ str(other))
        elif type(self.phase) != type(other.phase):
            raise TypeError("Phase types don't match: " + str(self) +", "+ str(other))
        return super().__eq__(other)

    def __sub__(self, other):
        if not hasattr(other, '_tick'):
            raise TypeError("Subtrahend must be have type 'GameTurn': "
                            + str( type( other ) ) + " " + str( other ) )
        if type(self._phase) != type(other.phase):
            raise TypeError( "Operands have different phase types: "
                             + str( type( self._phase ) ) + " - " + str( type( other.phase ) ) )
        return self._tick - other.tick

    def __hash__( self ) :
        return hash( self._tick )

    def __str__( self ) :
        string = "<"
        string += "[" + str( self.tick ) + "] "
        string += str( self.turn )
        if self._phase is not None :
            string += " " + str( self.phase.name.title() )

        string += ">"
        return string

    #####################

    def __next__( self ) :
        if self.stop_iteration is True :
            raise StopIteration

        next_time = deepcopy(self)
        if self._phase is not None:
            if self._phase.is_last:
                next_time._turn += 1
            next_time._tick += self._phase.duration
            next_time._phase = next(self._phase)

        elif self._phase is None:
            next_time._turn += 1
            next_time._tick += 1

        return next_time



#----------------------------------------------------------------------#

class Calendar:
    pass


#----------------------------------------------------------------------#

class CalendarScaling(Calendar) :
    pass



#----------------------------------------------------------------------#
