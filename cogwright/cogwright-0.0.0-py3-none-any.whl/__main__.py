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
from .make import authenticate_ftp, archive_path, download_payload
from .make import build_source

import logging

log = logging.getLogger( name="cogwright.__main__" )
log.debug = print

#----------------------------------------------------------------------#

Parameters = namedtuple( 'Parameters', [
    'tasks',
    'path_cwd',
    'path_download',
    'path_source',
    'path_payload'
] )

def command_line_parameters( argv ) :
    log.debug( "ARGV", argv )
    parser = argparse.ArgumentParser( description=__doc__ )

    ####################
    parser.add_argument(
        'tasks',
        type=str,
        nargs=argparse.REMAINDER,
        help='tasks to execute',
    )
    # ToDo: value checking

    parser.add_argument(
        '-D', '--download-path',
        dest='path_download',
        default="./download",
        help='store payload in this path, relative to repository root'
    )

    parser.add_argument(
        '-S', '--source-path',
        dest='path_source',
        default="./cogwright",
        help='path to target module'
    )

    parser.add_argument(
        '-O', '--payload-path',
        dest='path_payload',
        default="cogwright",
        help='store payload in this path, relative to build path'
    )

    ####################
    args = parser.parse_args( argv )

    # Configure Tasks
    tasks = set( args.tasks )
    if 'all' in tasks :
        tasks = tasks | { 'backup', 'download', 'build_package' }

    ### raise exception if paths don't exist ToDo: try to create paths
    path_cwd        = Path( os.getcwd( ) )
    path_download   = Path( args.path_download )
    path_source     = Path( args.path_source ).resolve( )
    path_payload    = path_source / args.path_payload

    parameters = Parameters( tasks, path_cwd, path_download, path_source, path_payload )
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
    (path_archive, _, extension) = archive_path( parameters.path_download )
    if 'download' in parameters.tasks :
        print( "download", path_archive )

        try :
            parameters.path_download.resolve( )
        except FileNotFoundError as e :
            parameters.path_download.mkdir( )

        ### download new distribution if required, ToDo upgrade optional
        (path_archive, extension) = download_payload( parameters.path_download, authenticate_ftp( ) )
        ###unzip

    if 'expand' in parameters.tasks :
        print( "expand" )

    if 'build_docs' in parameters.tasks :
        print( "docs" )

    if 'build_package' in parameters.tasks :
        print( "build" )
        build_source( path_archive, extension, parameters.path_download, parameters.path_source,
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
