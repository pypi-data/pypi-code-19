
'''
functions recognised inside yamlisp s-expressions
'''

from pathlib import Path
import sys
import contextlib
from .yaml import rprint

import logging
log = logging.getLogger( name="yamlisp.functions" )
log.debug = lambda *a, **b : None
# log.debug = print

#----------------------------------------------------------------------#

__all__ = []

def export( obj ) :
    __all__.append( obj.__name__ )
    return obj

#----------------------------------------------------------------------#

############################
class DelayedPath :
    """Stores a string that is only type-cast to Path when it is looked at"""

    def __init__( self, target ) :
        self._target = str(target)

    @property
    def target( self ) -> Path :
        return Path( self._target )

    @target.setter
    def target( self, other: str ) :
        self._target = other

    def __str__( self ) :
        return str( Path( self.target ) )

    def __repr__( self ) :
        return "<DelayedPath " + repr( Path( self.target ) ) + " >"

    def resolve(self):
        resolved_path   = Path(self._target).resolve()
        result          = type(self)( str(resolved_path) )
        return result


class PathList( list ) :
    path_delimeter = ';' if (sys.platform == "win32") else ':'

    def join( self ) :
        strings = [str( atom ) for atom in self]
        return self.path_delimeter.join( strings )


class PathList2( list ) :
    path_delimeter = ',' if (sys.platform == "win32") else ','

    def join( self ) :
        strings = [str( atom ) for atom in self]
        return self.path_delimeter.join( strings )

@contextlib.contextmanager
def modify_as_string(value):
    temporary_value = str(value)
    yield [temporary_value,]

    value = type(value)(temporary_value)


############################
@export
def _var( current_config, target_config, target_data, target_section_name, target_key, s_expression ) :
    """declare a variable of a static type"""
    result = None
    return result


@export
def _path( current_config, target_config, target_data, target_section_name, target_key, s_expression ) :
    """declare a variable of path type"""

    result = PathList(map(DelayedPath, s_expression[1:]))
    return result

@export
def _path2( current_config, target_config, target_data, target_section_name, target_key, s_expression ) :
    """declare a variable of path type"""

    print("PATHLIST2")
    result = PathList2(map(DelayedPath, s_expression[1:]))
    return result


############################
@export
def _append( current_config, target_config, target_data, target_section_name, target_key, s_expression, __prepend=False ):
    """append to a list type; transform a scalar into a list type and append to it"""

    args = s_expression[1:]

    target_section = target_data[target_section_name]
    target_value = target_section.get( target_key, list() )
    if s_expression == target_value:    # skip this operation during load_parameters; evaluate it during _add_section instead
        return s_expression

    result = target_value

    if isinstance( target_value, list): ################

        if __prepend:
            result = [*args, *result]
        else:
            result = [*result, *args]
        log.debug(result)

    elif isinstance( target_value, dict): ##############
        log.debug( "~~~~~~~ dict", target_value )

        # result = PathList(s_expression ).append( target_value )
        raise TypeError("appending to dict is not expected")

    else: ##########################################################
        log.debug( "~~~~~~~ else", target_value )
        result = PathList(target_value).extend(args)

    # except KeyError:
    #     log.debug( "~~~~~~~ KeyError")
        # log.debug(args)
        # rprint(target_data )
        # result = PathList(s_expression )

    log.debug("~~~~ RESULT:", result)
    log.debug("")
    return result


@export
def _prepend( current_config, target_config, target_data, target_section_name, target_key, s_expression ):
    return _append( current_config, target_config, target_data, target_section_name, target_key, s_expression, __prepend=True)


#----------------------------------------------------------------------#
############################
@export
def _importparent( current_config, target_config, target_data, target_section_name, target_key, s_expression ) :
    """read __omd__.yaml files in the paths in args, and import their keys as parents"""

    target_section  = target_data[target_section_name]
    target_value    = target_section.get( target_key, list( ) )
    # if s_expression == target_value :    # skip this operation during load_parameters; evaluate it during _add_section instead
    #     log.debug("!!!! DEFERRED !!!!")
    #     return s_expression


    log.debug("!!!! IMPORTPARENT !!!!")

    log.debug( "CONFIG", target_config )
    log.debug( "PARENTS", target_config.parents, )
    log.debug( "CHILDREN", target_config.children )

    import_path     = Path( s_expression[1] ).resolve( )
    parent_config   = type(target_config)( import_path / '__omd__.yaml' )

    new_config = current_config + parent_config
    current_config.rebase(new_config)
    current_config.parents[import_path] = parent_config

    return str(import_path)


############################
@export
def _import( current_config, target_config, target_data, target_section_name, target_key, s_expression ) :
    """read __omd__.yaml files in the paths in args, and attach them as a child node"""


    target_section  = target_data[target_section_name]
    target_value    = target_section.get( target_key, list( ) )
    if s_expression == target_value :    # skip this operation during load_parameters; evaluate it during _add_section instead
        log.debug("!!!! DEFERRED !!!!")
        return s_expression


    log.debug("!!!! IMPORT !!!!")

    log.debug( "CONFIG", target_config )
    log.debug( "PARENTS", target_config.parents, )
    log.debug( "CHILDREN", target_config.children )

    import_path     = Path( s_expression[1] ).resolve( )
    child_config    = type(target_config)( import_path / '__omd__.yaml' )
    child_config.finalize( import_path )

    current_config.children[import_path] = child_config

    return str(import_path)

#----------------------------------------------------------------------#

############################
@export
def _let( current_config, target_config, target_data, target_section_name, target_key, s_expression ) :
    """clause containing bound variables"""

    result = None

    return result


############################
@export
def _includeif( current_config, target_config, target_data, target_section_name, target_key, s_expression ) :
    """include the key only if the condition is true"""

    result = None

    return result


#----------------------------------------------------------------------#

############################
@export
def _ref( current_config, target_config, target_data, target_section_name, target_key, s_expression ) :
    """reference key-values in config nodes located on sibling branches within the inheritance hierarchy"""

    result = None

    return result


#----------------------------------------------------------------------#

