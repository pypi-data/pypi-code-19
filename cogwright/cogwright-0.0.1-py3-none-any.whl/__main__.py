#!python
#-- cogwright.__main__

"""
"""

import argparse
import os
import sys
import shutil

from pathlib import Path
from collections import namedtuple

from .make import backup_payload
from .make import archive_path, download_payload
from .make import build_source

import logging

log = logging.getLogger( name="cogwright.__main__" )
log.debug = print

sys.path.append(str(Path('.')))

#----------------------------------------------------------------------#

Parameters = namedtuple( 'Parameters', [
    'tasks',
    'path_cwd',
    'path_archive',
    'path_download',
    'path_source',
    'path_payload'
] )

def command_line_parameters( argv ) :
    log.debug( "ARGV", argv )
    parser = argparse.ArgumentParser( description=__doc__ )

    ####################

    parser.add_argument(
        '-A', '--archive_path',
        dest='path_archive',
        default=None,
        help='store payload in this path, relative to repository root'
    )

    parser.add_argument(
        'tasks',
        type=str,
        nargs=argparse.REMAINDER,
        help='tasks to execute',
    )
    # ToDo: value checking



    ####################
    args = parser.parse_args( argv )

    print("ARGS", args)

    # Configure Tasks
    tasks = set( args.tasks )
    if 'make' in tasks :
        tasks = tasks | { 'backup', 'download', 'build_package' }

    ### raise exception if paths don't exist ToDo: try to create paths
    path_cwd        = Path( os.getcwd( ) )
    path_archive    = args.path_archive
    path_download   = Path( './download' )

    import __blueprint__ as blueprint
    path_source     = blueprint.path_source
    path_payload    = blueprint.path_payload

    parameters = Parameters( tasks, path_cwd, path_archive, path_download, path_source, path_payload )
    return parameters

#----------------------------------------------------------------------#

def cog( parameters: Parameters ) -> True :
    """construct a python platform wheel out of a payload binary distribution"""

    #ToDo: replace with enum, values of which correspond with make functions

    if 'backup' in parameters.tasks :
        print( "backup", parameters.path_source )
        ### backup previous module/payload dir
        backup_payload( parameters.path_payload )

    # ToDo: clean this up
    print("parameters.path_archive", parameters.path_archive)
    (path_archive, _) = archive_path( parameters.path_download, parameters.path_archive )
    if 'download' in parameters.tasks :
        print( "download", path_archive )

        try :
            parameters.path_download.resolve( )
        except FileNotFoundError as e :
            parameters.path_download.mkdir( )

        ### download new distribution if required, ToDo upgrade optional
        path_archive = download_payload(    parameters.path_download,
                                            path_archive
                                       )
        ###unzip

    if 'expand' in parameters.tasks :
        print( "expand" )

    if 'build_docs' in parameters.tasks :
        print( "docs" )

    if 'build_package' in parameters.tasks :
        print( "build" )
        build_source( path_archive,
                      parameters.path_download,
                      parameters.path_payload )

    if 'test' in parameters.tasks :
        print( "test" )

    if 'clean' in parameters.tasks :
        print( "clean" )

    if 'install' in parameters.tasks :
        print( "install" )

    if 'install_dev' in parameters.tasks :
        print( "install_dev" )

    return True

#----------------------------------------------------------------------#

def main( ) :
    return cog( command_line_parameters( sys.argv[1 :] ) )

if __name__ == "__main__" :
    exit( main( ) )


#----------------------------------------------------------------------#
