
'''
process yaml files
'''

# https://gist.github.com/bowsersenior/979804

from pathlib import Path
from itertools import accumulate
from collections import OrderedDict

from ruamel.yaml import load, dump, MappingNode, constructor
try :
    from ruamel.yaml import CLoader as Loader, CDumper as Dumper

except ImportError :
    from ruamel.yaml import Loader, Dumper

from .path import temporary_working_directory


#----------------------------------------------------------------------#

# https://gist.github.com/enaeseth/844388
class OrderedDictYAMLLoader( Loader ) :
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__( self, *args, **kwargs ) :
        Loader.__init__( self, *args, **kwargs )

        self.add_constructor( u'tag:yaml.org,2002:map', type( self ).construct_yaml_map )
        self.add_constructor( u'tag:yaml.org,2002:omap', type( self ).construct_yaml_map )

    def construct_yaml_map( self, node ) :
        data = OrderedDict( )
        yield data
        value = self.construct_mapping( node )
        data.update( value )

    def construct_mapping( self, node, deep=False ) :
        if isinstance( node, MappingNode ) :
            self.flatten_mapping( node )
        else :
            raise constructor.ConstructorError(
                None, None,
                'expected a mapping node, but found %s' % node.id,
                node.start_mark )

        mapping = OrderedDict( )
        for key_node, value_node in node.value :
            key = self.construct_object( key_node, deep=deep )
            try :
                hash( key )
            except TypeError as exc :
                raise constructor.ConstructorError( 'while constructing a mapping',
                                                         node.start_mark, 'found unacceptable key (%s)' % exc,
                                                         key_node.start_mark )
            value = self.construct_object( value_node, deep=deep )
            mapping[key] = value
        return mapping


#----------------------------------------------------------------------#

def read( filename:Path ) :
    result = None
    with filename.open( ) as file:
        result = load(file, Loader=OrderedDictYAMLLoader )

    return result




#----------------------------------------------------------------------#

def fix_paths( struct, working_directory:Path ):
    """interpret keys beginning with PATH_ as Path objects; resolve them to absolute paths"""
    # Todo: eliminate mutability

    if isinstance( struct, list):
        for item in struct:
            fix_paths( item, working_directory )
    elif isinstance( struct, dict):
        for (key, value) in struct.items():
            if isinstance(value, dict):
                fix_paths(value, working_directory)
            elif isinstance( value, list) :
                fix_paths( value, working_directory )
            elif isinstance(value, str) and key[0 :5] == "PATH_" :
                try:
                    with temporary_working_directory( working_directory) as old_working_dir:
                        struct[key] = Path(value).resolve()
                except FileNotFoundError as e:
                    print("FILE NOT FOUND")
                    raise FileNotFoundError(e)
    return struct


#----------------------------------------------------------------------#

def indent(num:int, fill:str=' ') -> str:
    if num == 0:
        return ""
    return str( list(accumulate( fill for num in range(0, num) )) [-1])


def rprint( struct, i=0, quiet=False):
    #ToDo: return a string

    result = ""
    if isinstance( struct, list ) : # loop over list
        for value in struct :
            if isinstance( value, dict ) \
            or isinstance( value, list ) : # recurse on subsequence
                result += rprint( value, i + 2, quiet )

            else:
                line = indent( i ) + "- " + str( value )
                result += line + "\n"
                print( line ) if quiet is False else None

    elif isinstance( struct, dict ) : # loop over dict
        for (key, value) in struct.items( ) :
            line    = indent( i ) + "" + str( key ) + ": "
            result += line
            print( line, end='' ) if quiet is False else None

            if isinstance( value, dict ) \
            or isinstance( value, list ) : # recurse on subsequence
                print("") if quiet is False else None
                result += "\n"
                result += rprint( value, i + 2, quiet )

            else:
                result += str(value) + "\n"
                print( str(value) ) if quiet is False else None
    return result


#----------------------------------------------------------------------#
