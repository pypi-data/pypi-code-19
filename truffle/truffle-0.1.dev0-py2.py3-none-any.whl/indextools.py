"""
Author: Amol Kapoor
Description: Provides API for indexing code base.
"""

import json
import os

import global_constants as gc
import parsers.pyparser as pyparser
import text_index


def _get_parsers(files, root):
    """For each file in files, get the appropriate ast tree."""
    parsers = []
    for fname in files:
        parser = _map_file_to_parser(fname, root)
        parsers.append(parser)
    return parsers


def _map_file_to_parser(fname, root):
    """Return the right parser class."""
    # TODO: Make this do the right thing; right now only does python.
    if not fname.endswith('py'):
        raise ValueError('file type not implemented; check _map_file_to_parser')
    return pyparser.PyParser(fname, root)


def get_files(code_dir):
    """Gets a list of files that can be processed by truffle."""
    tfl_files = []
    total_files = []
    for (dirpath, _, filenames) in os.walk(code_dir):
        py_fnames = [os.path.join(dirpath, f) for f in filenames if
                     f.endswith(gc.SUPPORTED_LANGS)]
        tot_fnames = [os.path.join(dirpath, f) for f in filenames]
        tfl_files.extend(py_fnames)
        total_files.extend(tot_fnames)
    return tfl_files, total_files


def index_code(code_dir):
    """Gets a new project index object."""
    return ProjectIndex(code_dir)


class ProjectIndex(object):
    """Holds the index for the entire project."""

    def __init__(self, code_dir, index_fname='project_index.json'):
        self.root = code_dir
        self.files, self.total_files = get_files(code_dir)
        self.text_searcher = text_index.index_text(self.total_files)
        self.parsers = _get_parsers(self.files, self.root)
        self.project_index, self.functions = self._index_code()

        # Process calling functions.
        self._get_calling_functions()

        self.forest = self._get_forest()

        with open(index_fname, 'w') as f:
            json.dump(self.project_index, f)

    def _append_call(self, source, caller):
        """Appends call to source from caller in source function location."""
        for _, file_obj in self.project_index.iteritems():
            if source in file_obj['functions']:
                file_obj['functions'][source]['calling_functions'].append(
                    caller)
                break

    def _get_calling_functions(self):
        """Parses the project_index and adds calling functions."""
        for _, file_obj in self.project_index.iteritems():
            for _, call in file_obj['calls'].iteritems():
                source = call['source']
                caller = call['caller']
                self._append_call(source, caller)

    def _get_tree(self, func_name, func_obj):
        """Gets an individual call tree."""
        tree = {
            'name': func_name,
            'children': []
        }

        for call_name in func_obj['calls']:
            # Check to make sure its a user defined function.
            if call_name in self.functions:
                tree['children'].append(
                    self._get_tree(call_name, self.functions[call_name]))
            else:
                tree['children'].append({
                    'name': call_name,
                    'children': []
                })
        return tree

    def _get_forest(self):
        """Gets all of the individual call trees."""
        forest = []
        for func_name, func_obj in self.functions.iteritems():
            if not func_obj['calling_functions']:
                forest.append(self._get_tree(func_name, func_obj))
        return forest

    def _index_code(self):
        """Returns a list of index objects."""
        project_index = {}
        functions = {}
        for parser in self.parsers:
            file_index = parser.index_code()
            project_index[parser.fname] = file_index
            functions.update(file_index['functions'])
        return project_index, functions

    def get_text_search(self, query):
        """ Gets the text search hits """
        return text_index.search_text(self.text_searcher, query)

    def get_file_index(self, fname):
        """Gets an index for a file."""
        # Remove slashes.
        fname = fname.replace('/', '.')
        # Remove extension.
        fname = '.'.join(fname.split('.')[:-1])
        if fname in self.project_index:
            return self.project_index[fname], fname
        else:
            return None, None
