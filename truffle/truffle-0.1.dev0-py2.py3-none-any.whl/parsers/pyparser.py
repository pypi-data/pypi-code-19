"""
Author: Amol Kapoor
Description: Parser for .py files
"""

import ast
import pywalker


class PyParser(object):
    """Python file parser."""
    FILE_TYPE = '.py'

    def __init__(self, fname, root_dir):
        self.real_fname = fname
        try:
            self.root = ast.parse(open(fname, 'r').read())
        except SyntaxError:
            print 'File %s has invalid syntax, cannot be indexed' % self.fname
            self.root = None

        fname = '.'.join(fname.split('.')[:-1])  # Get rid of .py extension.
        self.fname = fname.replace('/', '.')
        self.root_dir = root_dir.replace('/', '.')

    def index_code(self):
        walker = pywalker.FileWalker(self.fname, self.root_dir)
        walker.visit(self.root)
        data = walker.get_data()
        return {
            'functions': data[0],
            'variables': data[1],
            'imported_modules': data[2],
            'imported_from': data[3],
            'calls': data[4]
        }
