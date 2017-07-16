#!/Anaconda3/python
# storytime

'''
description
'''

from enum import Enum

from .meta import equality_of

#----------------------------------------------------------------------#

class ThemeHandler :
    """
    Base class used to instantiate values of Theme enum members
    """

    def __init__( self, value=None ) :
        """Value is a general parameter whose interpretation is theme-dependant"""
        self.value = value

    def value( self, event, universe ) :
        print( self )
        raise NotImplementedError

    def target( self, event, universe ) :
        print( self )
        raise NotImplementedError

    def start_time( self, event, universe ) :
        print( self )
        raise NotImplementedError

    def end_time( self, event, universe ) :
        print( self )
        raise NotImplementedError

    def causes( self, event, universe ) :
        print( self )
        raise NotImplementedError

    def consequences( self, event, universe ) :
        print( self )
        raise NotImplementedError

    def participants( self, event, universe ) :
        print( self )
        raise NotImplementedError


#####################

from .actors import Feature

class __Theme( Feature ):
    NULL = 0
    HUNGER = 1


#####################
from .time import Cycle

class PlotAction( Cycle ):
    NONE = 0
    BACKGROUND = 1
    SETTING = 2
    INTRODUCTION = 3
    CONFLICT = 4
    RISING = 5
    CLIMAX = 6
    FALLING = 7
    RESOLUTION = 8
    EPILOGUE = 9


#----------------------------------------------------------------------#

from .time import GameTurn

class Event:
    """A thematic component of a causal network"""

    def __init__( self,
                  theme:Feature,
                  value = None,
                  target = None,
                  start_time: GameTurn = None,
                  end_time: GameTurn = None,
                  participants: list = None,
                  causes:list = None,
                  consequences:list = None,
                  index = None
                  ):

        self.index = index

        self.theme = theme
        self.value = value
        self.target = target

        self.start_time=start_time
        self.end_time=end_time

        # participants
        if participants is None :
            self.participants = list( )
        else :
            self.participants = participants

        # causes
        if causes is None :
            self.causes = list( )
        else :
            self.causes = causes

        # consequences
        if consequences is None :
            self.consequences = list( )
        else :
            self.consequences = consequences


    def __eq__(self,other):
        keys = ("index",)
        return equality_of(self, other, keys)


#----------------------------------------------------------------------#

class Context :
    pass


#----------------------------------------------------------------------#

class Fact :
    pass


#####################

class MemorySemantic :
    pass


#----------------------------------------------------------------------#

class Episode :
    pass


#####################

class MemoryEpisodic :
    pass


#----------------------------------------------------------------------#

class History:
    """Event Network"""

    def __init__(self, events:list=None):
        if events is None :
            self.events = list( )
        else :
            self.events = events


    def add_event(self, event:Event):
        index = len(self.events)
        event.index=index

        self.events.append(event)


    def __getitem__( self, index:int ):
        """
        return event by numerical index
        """
        if index is None:
            raise KeyError("null index: ")
        else:
            result = self.events[index]
            if result is None:
                raise KeyError("index returns None:", index)
            return result



#----------------------------------------------------------------------#
