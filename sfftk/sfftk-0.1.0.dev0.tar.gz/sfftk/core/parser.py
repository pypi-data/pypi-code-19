# -*- coding: utf-8 -*-
# parser.py
"""Parses command-line options"""

__author__  = 'Paul K. Korir, PhD'
__email__   = 'pkorir@ebi.ac.uk, paul.korir@gmail.com'
__date__    = '2016-06-10'


import argparse
import sys
from copy import deepcopy
import os
from sfftk.core.print_tools import print_date

verbosity_range = range(4)

Parser = argparse.ArgumentParser(prog='sff', description="The EMDB-SFF Toolkit (sfftk)")

subparsers = Parser.add_subparsers(
    title='Tools', 
    dest='subcommand', 
    description='The EMDB-SFF Toolkit (sfftk) provides the following tools:', 
    metavar="EMDB-SFF tools"
    )

#===============================================================================
# common arguments
#===============================================================================
primary_descriptors = {
    'args':['-P', '--primary-descriptor'],
    'kwargs': {
        'help': "populates the <primaryDescriptor>...</primaryDescriptor> to this value [valid values:  threeDVolume, contourList, meshList, shapePrimitiveList]"
        }
    }
output = {
    'args':['-o', '--output'],
    'kwargs': {
#         'type': argparse.FileType('w'),
        'default': None,
        'help': "file to convert to; the extension (.sff, .hff, .json) determines the output format [default: None]"
        }
    }
FORMAT_LIST = [
    ('sff', 'XML'),
    ('hff', 'HDF5'),
    ('json', 'JSON'),
    ]
# format_ = {
#     'args': ['-f', '--format'],
#     'kwargs': {
#         'default': 'sff', 
#         'help': "output file format; valid options are: {} [default: sff]".format(
#             ", ".join(map( lambda x: "{} ({})".format(x[0], x[1]), FORMAT_LIST))
#             ), 
#         }
#     }
verbose = {
    'args':['-v', '--verbose'],
    'kwargs': {
        'action': 'store_true', 
        'default': False, 
        'help': "verbose output"
        },
    }
config_path = {
    'args':['-c', '--config-path'],
    'kwargs': {
        'help': "path to configs file"
        }
    }
details_param = {
    'args':['-d', '--details'],
    'kwargs': {
        'default': "", 
        'help': "populates <details>...</details> in the XML file [default: '']"
        }
    }
transparency = {
    'args':['-t', '--transparency'],
    'kwargs': {
        'type': float, 
        'default': 1.0, 
        'help': "set the transparency on a scale of 0.0 (transparent) to 1.0 (opaque) [default: 1.0]"
        }
    }
sff_file = {
    'args': ['sff_file'],
    'kwargs': {
        'help': 'path (rel/abs) to an EMDB-SFF file',
        }
    }
segment_id = {
    'args': ['-i', '--segment-id'],
    'kwargs': {
        'help': 'refer to a segment by its ID'
        }
    }
description = {
    'args': ['-D', '--description'],
    'kwargs': {
        'help': 'the description'
        }
    }
number_of_instances = {
    'args': ['-n', '--number-of-instances'],
    'kwargs': {
        'type': int,
        'help': 'the number of instances',
        }
    }
external_ref = {
    'args': ['-E', '--external-ref'],
    'kwargs': {
        'nargs': 2,
        'help': "the type of external reference (a valid ontology short name \
e.g. 'omit') followed by the reference accession e.g. 'OMIT:0033410'",
        }
    }
external_ref_id = {
    'args': ['-e', '--external-ref-id'],
    'kwargs': {
        'type': int,
        'help': "the external reference ID as shown with the 'list' command",
        }
    }
complexes = {
    'args': ['-C', '--complexes'],
    'kwargs': {
        'help': "PDBe accession for complexes separated by commas without spaces \
between e.g. 'comp1,comp2,...,compN'",
        }
    }
complex_id = {
    'args': ['-c', '--complex-id'], 
    'kwargs': {
        'type': int, 
        'help': "the complex ID as shown with the 'list' command",
        }
    }
macromolecules = {
    'args': ['-M', '--macromolecules'],
    'kwargs': {
        'help': "PDBe accession for macromolecules separated by commas without \
spaces between e.g. 'macr1,macr2,...,macrN'",
        }
    }
macromolecule_id = {
    'args': ['-m', '--macromolecule-id'], 
    'kwargs': {
        'type': int, 
        'help': "the macromolecule ID as shown with the 'list' command",
        }
    }

notes_parser = subparsers.add_parser(
    'notes', 
    description="The EMDB-SFF Annotation Toolkit",
    help="annotate an EMDB-SFF file",
    )

notes_subparsers = notes_parser.add_subparsers(
    title='Annotation tools',
    dest='notes_subcommand',
    description='The EMDB-SFF Annotation Toolkit provides the following tools:',
    metavar="EMDB-SFF annotation tools",
    )

#===============================================================================
# convert subparser
#===============================================================================
convert_parser = subparsers.add_parser('convert', description="Perform conversions to EMDB-SFF", help="converts from/to EMDB-SFF")
convert_parser.add_argument('from_file', help="file to convert from")
# convert_parser.add_argument('output', default=None, help="file to convert to; the extension (.sff, .hff, .json) determines the output format [default: None]")
convert_parser.add_argument('-x', '--exclude-unannotated-regions', action='store_true', default=False, help="(only for Segger) exclude regions with no annotation [default: False]")
convert_parser.add_argument('-t', '--top-level-only', default=False, action='store_true', help="convert only the top-level segments [default: False]")
convert_parser.add_argument('-M', '--contours-to-mesh', default=False, action='store_true', help="convert an 'contourList' EMDB-SFF to a 'meshList' EMDB-SFF")
convert_parser.add_argument(*output['args'], **output['kwargs'])
# convert_parser.add_argument(*format_['args'], **format_['kwargs'])
convert_parser.add_argument(*details_param['args'], **details_param['kwargs'])
convert_parser.add_argument(*primary_descriptors['args'], **primary_descriptors['kwargs'])
convert_parser.add_argument(*verbose['args'], **verbose['kwargs'])

#===============================================================================
# config subparser
#===============================================================================
config_parser = subparsers.add_parser('config', description="Write configs used by updateschema and OMERO-server connection", help="manage configs")
config_parser.add_argument('config_name', help="name of config to write")
config_parser.add_argument('config_value', help="value of config to write")

#===============================================================================
# view subparser
#===============================================================================
view_parser = subparsers.add_parser('view', description="View a summary of an SFF file", help="view file summary")
view_parser.add_argument('from_file', help="any SFF file")
view_parser.add_argument('-V', '--version', action='store_true', help="show SFF format version")
view_parser.add_argument(*verbose['args'], **verbose['kwargs'])

#===============================================================================
# notes: search
#===============================================================================
search_notes_parser = notes_subparsers.add_parser(
    'search', 
    description="Search ontologies for annotation by text labels",
    help="search for terms by labels",
    )
search_notes_parser.add_argument('search_term', help="the term to search; add quotes if spaces are included")
search_notes_parser.add_argument('-r', '--rows', type=int, default=10, help="number of rows")
search_notes_parser.add_argument('-s', '--start', type=int, default=1, help="start index")
search_notes_parser.add_argument('-O', '--ontology', default=None, help="the ontology to search [default: None]")
search_notes_parser.add_argument('-x', '--exact', default=False, action='store_true', help="exact matches? [default: False]")
search_notes_parser.add_argument('-o', '--obsoletes', default=False, action='store_true', help="include obsoletes? [default: False]")
search_notes_parser.add_argument('-L', '--list-ontologies', default=False, action='store_true', help="list available ontologies [default: False]")
search_notes_parser.add_argument('-l', '--short-list-ontologies', default=False, action='store_true', help="short list of available ontologies [default: False]")

#===============================================================================
# notes: suggest
#===============================================================================
"""
:TODO: suggest terms from a description
"""
# TBA

#===============================================================================
# notes: list
#===============================================================================
list_notes_parser = notes_subparsers.add_parser(
    'list',
    description="List all available annotations present in an EMDB-SFF file",
    help="list available annotations",
    )
list_notes_parser.add_argument(*sff_file['args'], **sff_file['kwargs'])
list_notes_parser.add_argument('-l', '--long-format', default=False, action='store_true', help="only show segment ID and description (if present)")

#===============================================================================
# notes: show
#===============================================================================
show_notes_parser = notes_subparsers.add_parser(
    'show',
    description="Show a specific annotations by ID present in an EMDB-SFF file",
    help="show an annotation by ID",
    )
show_notes_parser.add_argument(*sff_file['args'], **sff_file['kwargs'])
show_notes_parser.add_argument('-l', '--long-format', default=False, action='store_true', help="only show segment ID and description (if present)")
show_segment_id = deepcopy(segment_id)
show_segment_id['kwargs']['help'] += "; pass more than one ID as a comma-separated list with no spaces e.g. 'id1,id2,...,idN'"
show_notes_parser.add_argument(*show_segment_id['args'], **show_segment_id['kwargs'])

#===============================================================================
# notes:add
#===============================================================================
add_notes_parser = notes_subparsers.add_parser(
    'add',
    description="Add a new annotation to an EMDB-SFF file",
    help="add new annotations",
    )
add_notes_parser.add_argument(*sff_file['args'], **sff_file['kwargs'])
add_notes_parser.add_argument(*segment_id['args'], **segment_id['kwargs'])
add_notes_parser.add_argument(*description['args'], **description['kwargs'])
add_notes_parser.add_argument(*number_of_instances['args'], **number_of_instances['kwargs'])
external_ref['kwargs']['action'] = 'append'
add_notes_parser.add_argument(*external_ref['args'], **external_ref['kwargs'])
del external_ref['kwargs']['action']
add_notes_parser.add_argument(*complexes['args'], **complexes['kwargs'])
add_notes_parser.add_argument(*macromolecules['args'], **macromolecules['kwargs'])

#===============================================================================
# notes: edit
#===============================================================================
edit_notes_parser = notes_subparsers.add_parser(
    'edit',
    description="Edit an existing annotation to an EMDB-SFF file",
    help="edit existing annotations",
    )
edit_notes_parser.add_argument(*sff_file['args'], **sff_file['kwargs'])
edit_notes_parser.add_argument(*segment_id['args'], **segment_id['kwargs'])
edit_notes_parser.add_argument(*description['args'], **description['kwargs'])
edit_notes_parser.add_argument(*number_of_instances['args'], **number_of_instances['kwargs'])
external_ref['kwargs']['action'] = 'append'
edit_notes_parser.add_argument(*external_ref['args'], **external_ref['kwargs'])
del external_ref['kwargs']['action']
edit_notes_parser.add_argument(*external_ref_id['args'], **external_ref_id['kwargs'])
edit_notes_parser.add_argument(*complexes['args'], **complexes['kwargs'])
edit_notes_parser.add_argument(*complex_id['args'], **complex_id['kwargs'])
edit_notes_parser.add_argument(*macromolecules['args'], **macromolecules['kwargs'])
edit_notes_parser.add_argument(*macromolecule_id['args'], **macromolecule_id['kwargs'])

#===============================================================================
# notes: del
#===============================================================================
del_notes_parser = notes_subparsers.add_parser(
    'del',
    description="Delete an existing annotation to an EMDB-SFF file",
    help="delete existing annotations",
    )
del_notes_parser.add_argument(*sff_file['args'], **sff_file['kwargs'])
del_notes_parser.add_argument(*segment_id['args'], **segment_id['kwargs'])
description['kwargs'] = {
    'action': 'store_true',
    'default': False,
    'help': 'delete the description [default: False]',
    }
del_notes_parser.add_argument(*description['args'], **description['kwargs'])
del number_of_instances['kwargs']['type']
number_of_instances['kwargs'] = {
    'action': 'store_true',
    'default': False,
    'help': 'delete the number of instances [default: False]',
    }
del_notes_parser.add_argument(*number_of_instances['args'], **number_of_instances['kwargs'])
del_notes_parser.add_argument(*external_ref_id['args'], **external_ref_id['kwargs'])
del_notes_parser.add_argument(*complex_id['args'], **complex_id['kwargs'])
del_notes_parser.add_argument(*macromolecule_id['args'], **macromolecule_id['kwargs'])
# del_notes_parser.add_argument('-a', '--all', default=False, action='store_true', help="delete all annotations [USE WITH CAUTION!!!]")


#=============================================================================
# notes: merge
#=============================================================================
merge_notes_parser = notes_subparsers.add_parser(
    'merge',
    description="Merge notes from two EMDB-SFF files",
    help="merge notes from two EMDB-SFF files"
    )
merge_notes_parser.add_argument('sff_file1', help="first EMDB-SFF file")
merge_notes_parser.add_argument('sff_file2', help="second EMDB-SFF file")
merge_notes_parser.add_argument(*output['args'], **output['kwargs'])
merge_notes_parser.add_argument(*verbose['args'], **verbose['kwargs'])


#===============================================================================
# notes: save
#===============================================================================
save_notes_parser = notes_subparsers.add_parser(
    'save',
    description="Save all changes made to the actual file",
    help="write all changes made until the last 'save' action"
    )
save_notes_parser.add_argument(*sff_file['args'], **sff_file['kwargs'])

#===============================================================================
# notes: trash
#===============================================================================
trash_notes_parser = notes_subparsers.add_parser(
    'trash',
    description="Discard all notes by deleting the temporary file",
    help="discard all changes made since the last the edit action (add, edit, del)",
    )
trash_notes_parser.add_argument(*sff_file['args'], **sff_file['kwargs'])

# get the full list of tools from the Parser object
tool_list = Parser._actions[1].choices.keys()
tool_list += ['parser', 'sffreader', 'meshreader', 'surfreader', 'modreader', 'omero_wrapper', 'meshtools', 'stlreader', 'mapreader']

# tests
test_help = "one or none of the following: {}".format(", ".join(tool_list))
tests_parser = subparsers.add_parser('tests', description="Run unit tests", help="run unit tests")
tests_parser.add_argument('tool', nargs='*', default='all', help=test_help)
tests_parser.add_argument('-v', '--verbosity', default=1, type=int, help="set verbosity; valid values: %s [default: 0]" % ", ".join(map(str, verbosity_range)))

test_parser = subparsers.add_parser('test', description="Run unit tests", help="run unit tests")
test_parser.add_argument('tool', nargs='*', default='all', help=test_help)
test_parser.add_argument('-v', '--verbosity', default=1, type=int, help="set verbosity; valid values: %s [default: 0]" % ", ".join(map(str, verbosity_range)))

# parser function
def parse_args(_args):
    """
    Parse and check command-line arguments
    
    Subcommand handlers defined in __main__.py (e.g. handle_conver(...)) should not have to check arguments for consistency
    
    :param list _args: list of arguments
    :return: parsed arguments
    :rtype: `argparse.Namespace`
    """
    from sfftk.core.configs import get_configs
    configs = get_configs()
    # if we have no subcommands then show the available tools
    if len(_args) == 0:
        Parser.print_help()
        sys.exit(0)
    # if we only have a subcommand then show that subcommand's help
    elif len(_args) == 1:
        if _args[0] in Parser._actions[1].choices.keys():
            exec('{}_parser.print_help()'.format(_args[0]))
            sys.exit(0)
    # if we have 'notes' as the subcommand and a sub-subcommand show the options for that sub-subcommand
    elif len(_args) == 2:
        if _args[0] == 'notes':
            if _args[1] in Parser._actions[1].choices['notes']._actions[1].choices.keys():
                exec('{}_notes_parser.print_help()'.format(_args[1]))
                sys.exit(0)
    # parse arguments
    args = Parser.parse_args(_args)
    
    # check values
    # convert
    if args.subcommand == 'convert':
        try:
            assert os.path.exists(args.from_file)
        except AssertionError:
            print_date("File {} was not found".format(args.from_file))
            sys.exit(1)
        # set the output file
        if args.output is None:
            import re
            dirname = os.path.dirname(args.from_file)
            if re.match(r'.*\.sff$', args.from_file): # convert file.sff to file.hff
                fn = "".join(os.path.basename(args.from_file).split('.')[:-1]) + '.hff'
                args.__setattr__('output', os.path.join(dirname, fn))
            elif re.match(r'.*\.hff$', args.from_file): # convert file.hff to file.sff
                fn = "".join(os.path.basename(args.from_file).split('.')[:-1]) + '.sff'
                args.__setattr__('output', os.path.join(dirname, fn))
            else: # convert file.xxx to file.sff
                fn = "".join(os.path.basename(args.from_file).split('.')[:-1]) + '.sff'
                args.__setattr__('output', os.path.join(dirname, fn))
            if args.verbose:
                print_date("Seting output file to {}".format(args.output))
#         assert args.format in map(lambda x: x[0], FORMAT_LIST)
        
        # special handling of HDF5 file
#         if args.format == 'hff':
#             if args.output is None:
#                 raise ValueError("You must specify an actual filename to use hff (HDF5)")
#             else:
#                 import h5py
#                 args.output = h5py.File(args.output.name, 'w')
        
        # ensure valid primary_descriptor
#         if args.primary_descriptor:
#             try:
#                 assert args.primary_descriptor in ['threeDVolume', 'contourList', 'meshList', 'shapePrimitive']
#             except:
#                 raise ValueError('Invalid value for primaryDescriptor: %s' % args.primary_descriptor)
#         if args.verbose:
#             print_date("Found valid primary descriptor: {}".format(args.primary_descriptor))
        
    # tests
    elif args.subcommand == 'tests' or args.subcommand == 'test':        
        if isinstance(args.tool, list):
            for tool in args.tool:
                try:
                    assert tool in tool_list
                except AssertionError:
                    print >> sys.stderr, "Unknown tool: {}".format(tool)
                    print >> sys.stderr, "Available tools for test: {}".format(", ".join(tool_list))
        if args.verbosity:
            try:
                assert args.verbosity in range(4)
            except:
                raise ValueError("Verbosity should be in %s-%s: %s given" % (verbosity_range[0], verbosity_range[-1], args.verbosity))
    # notes
    elif args.subcommand == 'notes':
#         # ensure the file exists otherwise fail
#         if not os.path.exists(args.sff_file):
#             print_date("SFF file {} does not exist. Retry.".format(args.sff_file))
#             sys.exit(1)
        
        # convenience: the user can use '-' to refer to an EMDB-SFF file whch is the previous
        # file that was edited ('add', 'edit', 'del') 
        temp_file = configs['__TEMP_FILE']
        temp_file_ref = configs['__TEMP_FILE_REF']
        if args.notes_subcommand in ['list', 'show', 'add', 'edit', 'del', 'trash']:
            # find, view
            if args.notes_subcommand in ['list', 'show', 'search']:
                if args.sff_file == temp_file_ref:
                    if os.path.exists(temp_file):
                        args.sff_file = temp_file
                        print_date("Working on temp file {}".format(temp_file), stream=sys.stdout)
                    else:
                        print_date("Temporary file {} does not exist. \
Try invoking an edit ('add', 'edit', 'del') action on a valid EMDB-SFF file.".format(temp_file), stream=sys.stdout)
                        return None
                else:
                    print_date("Reading directly from {}".format(args.sff_file), stream=sys.stdout)
            # modify
#             elif args.notes_subcommand in ['add', 'edit', 'del']:
#                 if args.sff_file == temp_file_ref:
#                     if os.path.exists(temp_file):
#                         args.sff_file = temp_file
#                     else:
#                         print_date("Temporary file {} does not exist. \
# Try invoking an edit ('add', 'edit', 'del') action on a valid EMDB-SFF file.".format(temp_file), stream=sys.stdout)
#                         return None
#                 else:
#                     if os.path.exists(temp_file):
#                         print_date("Found temp file {}. Either run 'save' or 'trash' to \
# discard changes before working on another file.".format(temp_file), stream=sys.stdout)
#                         return None
#                     else:
#                         # copy the actual file to the temp file
#                         import shutil
#                         print_date("Edits to be made.", stream=sys.stdout)
#                         print_date("Copying {} to temp file {}...".format(args.sff_file, temp_file), stream=sys.stdout)
#                         shutil.copy(args.sff_file, temp_file)
#                         args.sff_file = temp_file
        else:
            pass
            
        if args.notes_subcommand == "show":
            try:
                assert args.segment_id
            except AssertionError:
                print_date("Please specify a segment ID")
                return None
            
            args.segment_id = map(int, args.segment_id.split(','))
        
        elif args.notes_subcommand == "add":
            try:
                assert args.segment_id
            except AssertionError:
                print_date("Please specify a segment ID")
                return None
                        
            args.segment_id = map(int, args.segment_id.split(','))
            
            # ensure we have at least one item to add
            try:
                assert (args.description is not None) or (args.number_of_instances is not None) or \
                (args.external_ref is not None) or (args.complexes is not None) or \
                (args.macromolecules is not None)
            except AssertionError:
                print_date("Nothing specified to add. Use one or more of the following options:\n\t-D <description> \n\t-E <extrefType> <extrefValue> \n\t-C cmplx1,cmplx2,...,cmplxN \n\t-M macr1,macr2,...,macrN \n\t-n <int>")
                return None
            
            # replace the string in args.complexes with a list
            if args.complexes:
                args.complexes = args.complexes.split(',')
            
            # ditto
            if args.macromolecules:
                args.macromolecules = args.macromolecules.split(',')
            
            # external ref consistency
            if len(args.external_ref) == 2 and isinstance(args.external_ref[0], str):
                args.external_ref = [args.external_ref]
        
        elif args.notes_subcommand == "edit":
            try:
                assert args.segment_id is not None
            except AssertionError:
                print_date("Please specify a segment ID", stream=sys.stdout)
                return None
            
            args.segment_id = map(int, args.segment_id.split(','))
            
            # replace the string in args.complexes with a list
            if args.complexes:
                args.complexes = args.complexes.split(',')
             
            # ditto
            if args.macromolecules:
                args.macromolecules = args.macromolecules.split(',')
            
            if args.external_ref:
                try:
                    assert args.external_ref_id is not None
                except AssertionError:
                    print_date("Will not be able to edit an external reference without \
specifying an external reference ID. Run 'list' or 'show' to see available \
external reference IDs for {}".format(args.segment_id), stream=sys.stdout)
                    return None
            
                # consistency of format
                if len(args.external_ref) == 0 and isinstance(args.external_ref[0], str):
                    args.external_ref = [args.external_ref]
            
            if args.complexes:
                try:
                    assert args.complex_id is not None
                except AssertionError:
                    print_date("Will not be able to edit a complex without specifying \
a complex ID. Run 'list' or 'show' to see available complex \
IDs for {}".format(args.segment_id), stream=sys.stdout)
                    return None
            
            if args.macromolecules:
                try:
                    assert args.macromolecule_id is not None
                except AssertionError:
                    print_date("Will not be able to edit a macromolecule without specifying\
a macromolecule ID. Run 'list' or 'show' to see available \
macromolecule IDs for {}".format(args.segment_id), stream=sys.stdout)
                    return None
                    
        elif args.notes_subcommand == "del":
            try:
                assert args.segment_id is not None
            except AssertionError:
                print_date("Please specify a segment ID", stream=sys.stdout)
                return None
            
            args.segment_id = map(int, args.segment_id.split(','))
            
            # ensure we have at least one item to add
            assert args.description or args.number_of_instances or \
                (args.external_ref_id is not None) or (args.complex_id is not None) or \
                (args.macromolecule_id is not None)
                
    return args 