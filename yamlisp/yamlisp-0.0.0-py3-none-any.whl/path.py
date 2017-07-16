

import contextlib
import os
from copy import deepcopy
from pathlib import Path

import logging
log = logging.getLogger( name="yamlisp.path" )
log.debug = lambda *a,**b : None
# log.debug = print

#----------------------------------------------------------------------#

def files_in(target_path: Path) -> list :
    files = [file for file in target_path.iterdir() if file.is_file()]
    return files

def subdirectories_of( target_path: Path ) -> list :
    subdirs = [subdir for subdir in target_path.iterdir( ) if subdir.is_dir()]
    return subdirs

def stack_of_files( target_path: Path, file: str ) -> list :
    lists_of_files = [list( parent.glob( file ) )
                      for parent in reversed([target_path, *target_path.parents])
                      ]
    return lists_of_files


#----------------------------------------------------------------------#

def paths2string(paths_list:list) -> str:
    """???"""
    result  = '"'
    count   = 0
    length  = len(paths_list)
    for path in paths_list:
        count += 1
        if count==length:
            result += str( path ) + ", "
        else:
            result += str( path )
    result += '"'
    return result


#----------------------------------------------------------------------#

@contextlib.contextmanager
def temporary_working_directory( path: Path ) :
    """change working directory to 'path' for the duration of the context manager"""

    old_working_dir = Path( os.getcwd( ) )

    # log.debug( "dir ->", str( path ) )
    os.chdir( str( path ) )
    yield old_working_dir

    # log.debug( "dir <-", str( old_working_dir ) )
    os.chdir( str( old_working_dir ) )


#----------------------------------------------------------------------#

def try_resolve( key, value, path:Path ):
    """"""

    log.debug( "TRY RESOLVE--------", type( value ), value )
    if isinstance( value, list ):
        return value

    value = str( value )
    ### attempt to resolve paths
    result = value
    try :
        log.debug("~~~ BEGIN")
        value_as_path = Path( str(value) )
        if value_as_path.exists( ) :
            with temporary_working_directory( path ) as old_working_dir :
                result      = str( value_as_path.resolve( ) )

    except FileNotFoundError as e :
        log.debug( "File Not Found", value )
        raise FileNotFoundError( e )
    except OSError as e:
        pass

    log.debug("RESOLVED", result)
    return result


#----------------------------------------------------------------------#


# ToDo: Path-addressable Dictionary
