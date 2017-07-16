#!/Anaconda3/python
# storytime

'''
utilities
'''

#ToDo: Load Enumeration values from XML file

#----------------------------------------------------------------------#

def some_function():
    pass
Function = type( some_function() )
del some_function

#----------------------------------------------------------------------#
def IdGenerator( count: int = 0, step: int = 1 ) :
    """list of integers for ID numbers"""
    while True :
        yield count
        count += step

#----------------------------------------------------------------------#

class Cache :
    """
    Defer evaluation until the first time the value is accessed
    Then store the value and return it on future access attempts
    Unless the condition callback evaluates to True, in which case recalculate
    """

    def __init__( self, key=None, value=None, update_method=None, condition=None ) :
        self._update_method = update_method
        self._condition = condition
        self._value = value
        if value is None :
            self._dirty = True
        else :
            self._dirty = False

    def dirty( self ) :
        self._dirty = True

    def clean( self ) :
        self._dirty = False

    @property
    def value( self ) :
        if self._dirty or self._condition is not None and self._condition( self ) :
            self._value = self._update_method( self._value )
            self.clean( )
        return self._value


class CacheArray(Cache):
    """Cache each element of an array"""
    pass

class CacheDict(Cache):
    """Cache a value for each key """
    pass
    #ToDo: This one can be used for GraphMatrix, key = (args, kwargs)


#----------------------------------------------------------------------#
    ### magic methods

def equality_of( self, other,  key:tuple ):
    """equal if keys exist and _function_tag values are equal"""

    assert self is not None
    assert other is not None
    assert key is not None
    assert key is not []

    is_equal = True
    for attribute_name in key:
        if not hasattr(self,attribute_name):
            raise TypeError("__eq__: self is missing required _function_tag: " + attribute_name)
        if not hasattr(other,attribute_name):
            is_equal = False
        if getattr( self, attribute_name ) != getattr( other, attribute_name ):
            is_equal = False
    return is_equal


#####################

def interface_of( self, other, attributes:tuple ):
    """interface shared if attributes exist on both objects"""

    assert self is not None
    assert other is not None
    assert attributes is not None
    assert attributes is not []

    shares_interface = True
    for attribute_name in attributes :
        if not hasattr( self, attribute_name ) :
            raise TypeError( "__eq__: self is missing required interface attribute: " + attribute_name )
        if not hasattr( other, attribute_name ) :
            shares_interface = False
    return shares_interface


#----------------------------------------------------------------------#
    ### attribute assignment

import inspect
from copy import deepcopy as _deepcopy

def prepare_object( parameter, cls=object, deepcopy=False, args=None, **kwargs ) :
    """__init__ default object if None; strict type"""

    obj = None
    if parameter is None :                  # default object
        if args is None :
            args = list( )
        obj = cls(*args, **kwargs)
    # if isinstance(parameter, type):
    #     if args is None :
    #         args = list( )
    #     obj = parameter( *args, **kwargs )
    elif inspect.isclass(cls):
        if isinstance( parameter, cls ) :   # strict type
            if deepcopy:
                obj = _deepcopy(parameter)
            else:
                obj = parameter
        else:
            raise TypeError( "object parameter must be " + str( cls ) + ", or None: " + str( parameter ) )
    else :
        raise TypeError( "cls must be a class: " + str( cls ) )
    return obj


#####################

import numpy as np

def prepare_ndarray( parameter=None, dim: int = 0, **kwargs) :
    """assign 1d ndarray. convert if list, initialize with shape=(dim,) if None"""

    vector = None
    if parameter is None :
        vector = np.zeros( dim )
    elif isinstance( parameter, list ) :
        vector = np.array( parameter, **kwargs )
    elif isinstance( parameter, np.ndarray ) :
        vector = parameter
    else :
        raise TypeError( "vector parameter must be list, ndarray, or None: " + str( parameter ) )

    if vector.ndim != 1 :
        raise ValueError( "vector must have ndim=1: " + str( vector ) )
    return vector


#####################

def append( target: np.ndarray, item ) :
    """append to numpy array"""
    return np.append( target, [item] )


#----------------------------------------------------------------------#
    ### Profiling

from datetime import datetime
from collections import OrderedDict

MILLION = 1000000
class Profiler:
    """decorator to record function runtimes and report them later"""

    def __init__(self):
        self._total_times = OrderedDict( )
        self._tags = OrderedDict( )
        # ToDo: max, min, count

    def reset(self):
        self.__init__()

    @staticmethod
    def _function_tag( function:Function ) -> str :
        key = str( function.__module__ ) + "." + str( function.inner_function.__name__ )
        return key

    def _add_runtime( self, tag_name, start:datetime, end:datetime ) :
        duration = end - start
        duration_micro = duration.microseconds + duration.seconds * MILLION
        self._total_times[tag_name] += duration_micro
        return duration_micro


    #####################
    def __call__( self, target ) :
        """dynamic dispatch to type-specific decorators"""

        if type( target ).__name__ == 'function' :
            return self._function( target )
        if type( target ).__name__ == 'type' :
            return self._class( target )
        else :
            raise ValueError( "Unsupported profile target:", target )


    def _function( self, function:Function ):
        """compute total runtime of a function"""

        tag_name = None # will be assigned after profiled_function is declared
        def profiled_function( *args, **kwargs ) :
            start = datetime.now( )
            result = function( *args, **kwargs )             # execute original function
            end = datetime.now( )
            self._add_runtime( tag_name, start, end )
            return result

        profiled_function.inner_function = function         # remember the inner function, for self._function_tag()
        tag_name = self._function_tag( profiled_function )  # allows profiled_function to reference itself
        self._total_times[tag_name] = 0                     # all runtimes for the same tag_name are summed together

        return profiled_function

    # ToDo: profile_class can add an attribute to methods that profiled_function can look for, then update initialization of _total_time.
    def _class( self, cls ) :
        """prepare methods of the class for profiling"""
        self._total_times.items( )
        return cls


    #####################
    def tag_start( self, tag_name ) :
        if tag_name not in self._tags.keys( ):
            self._total_times[tag_name] = 0
            self._tags[tag_name] = None

        elif self._tags[tag_name] is not None:
            raise RuntimeError("Timer started again while already running:", tag_name )

        self._tags[tag_name] = datetime.now()


    def tag_stop( self, tag_name ) :
        if self._tags[tag_name] is None :
            raise RuntimeError( "Timer stopped before starting:", tag_name )

        start = self._tags[tag_name]
        end = datetime.now()
        self._add_runtime(tag_name, start, end )
        self._tags[tag_name] = None


    #####################
    def report( self ) -> str :
        """construct runtime report in seconds"""

        string = "<Profile: \n"
        for (function, runtime) in self._total_times.items( ) :
            string += str( runtime / MILLION ) + " " + str( function ) + "\n"
        string += ">\n"
        return string


    def time( self, target ) -> float :
        """return runtime in seconds for a given function or tag name"""

        tag_name = None
        if type(target).__name__ == "function":
            tag_name = self._function_tag( target )
        if type( target ).__name__ == "method" :
            tag_name = self._function_tag( target ) # ToDo: Method-specific tag
        elif isinstance(target, str):
            tag_name = target
        return self._total_times[tag_name] / MILLION


#####################
profile = Profiler()


#----------------------------------------------------------------------#
    ### Weird meta shit

class FunctionStrictType :
    """
    function decorator that enforces types specified in annotations
    None matches all types
    """

    def __init__(self, function):
        self._function = function

    def __call__(self, *args, **kwargs):
        """raise exception if type does not match annotation"""

        for (param_name, param_type ) in self._function.__annotations__.items():
            pass
            #ToDo: check type and raise exception

        return self._function(*args, **kwargs)


#####################

def introspective( function ) :
    """
    decorator for declaring self-referential functions
    include 'me' as the first parameter to the inner function
    from exterior scope, refer to original function using __inner__ attribute
    """

    def introspective_function( *args, **kwargs ) :
        return function( function, *args, **kwargs )

    introspective_function.__inner__ = function  # allows access to original function from outside
    return introspective_function


def introspectivemethod( function ) :
    """
    decorator for declaring self-referential methods
    include 'me' as the second parameter to the inner function
    from exterior scope, refer to original function using __inner__ attribute
    """

    def introspective_method( self, *args, **kwargs ) :
        return function( self, function, *args, **kwargs )

    introspective_method.__inner__ = function
    return introspective_method


def introspective2( function ) :
    """
    decorator for declaring self-referential functions
    include 'me' as the first parameter to the inner function
    me.inner_function will retrieve the original function
    this version isn't as nice to use like this, but demonstrates a useful technique
    """

    me = None
    def introspective_function( *args, **kwargs ) :
        return function( me, *args, **kwargs )

    me = introspective_function # this is the value that gets passed to function
    me.__inner__ = function # allows access to original function from inside (and outside)
    return introspective_function


#----------------------------------------------------------------------#



