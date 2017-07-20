"""Tests for indextools.py."""

import indextools
import unittest

class testPywalker(unittest.TestCase):

    def test_get_files(self):

        pyfiles, tot_files = indextools.get_files(
            'test_data/get_files_test_data/')

        true_pyfiles = ['test_data/get_files_test_data/test4.py',
                        'test_data/get_files_test_data/test2.py',
                        'test_data/get_files_test_data/test1.py',
                        'test_data/get_files_test_data/dir1/test1.py']
        true_totfiles = true_pyfiles + [
            'test_data/get_files_test_data/test3.js',
            'test_data/get_files_test_data/dir1/test2.js']
        self.assertItemsEqual(pyfiles, true_pyfiles)
        self.assertItemsEqual(tot_files, true_totfiles)

    def test_index_code(self):
        """Read through all of the code in test_data/index_test_data, and test.

        Checks against functions, vars, imports, calls. Also call graph.
        """
        project_index = indextools.ProjectIndex('test_data/index_test_data')
        forest = project_index.forest
        project_index_funcs = project_index.functions
        project_index = project_index.project_index

        true_keys = ['test_data.index_test_data.test1',
                     'test_data.index_test_data.test2']
        self.assertItemsEqual(project_index.keys(), true_keys)

        functions = project_index[true_keys[0]]['functions']
        var = project_index[true_keys[0]]['variables']
        import_mod = project_index[true_keys[0]]['imported_modules']
        import_from = project_index[true_keys[0]]['imported_from']
        calls = project_index[true_keys[0]]['calls']

        true_functions = [true_keys[0] + '.add',
                          true_keys[0] + '.mult',
                          true_keys[0] + '.MathStuff',
                          true_keys[0] + '.MathStuff.__init__',
                          true_keys[0] + '.MathStuff.get_vars',
                          true_keys[0] + '.MathStuff.plug_in_vars']
        self.assertItemsEqual(true_functions, functions.keys())
        self.assertItemsEqual(true_functions, project_index_funcs)

        true_func_obj = {
            'args': ['x', 'y'],
            'lineno': 9,
            'calls': {},
            'fname': 'test_data.index_test_data.test1',
            'scope': '',
            'calling_functions': ['test_data.index_test_data.test2.14',
                                  'test_data.index_test_data.test2.16'],
            'docstring': 'This is a multiplication function for testing.',
            'name': 'mult'
        }

        self.assertDictEqual(true_func_obj, functions[true_keys[0] + '.mult'])

        true_vars = {
            true_keys[0] + '.x': true_keys[0] + '.x.3',
            true_keys[0] + '.x.3': true_keys[0] + '.x.3',
            true_keys[0] + '.add.x': true_keys[0] + '.x.5',
            true_keys[0] + '.add.x.5': true_keys[0] + '.x.5',
            true_keys[0] + '.add.y': true_keys[0] + '.y.5',
            true_keys[0] + '.add.y.5': true_keys[0] + '.y.5',
            true_keys[0] + '.add.x.7': true_keys[0] + '.x.5',
            true_keys[0] + '.add.y.7': true_keys[0] + '.y.5',
            true_keys[0] + '.mult.x': true_keys[0] + '.x.9',
            true_keys[0] + '.mult.x.9': true_keys[0] + '.x.9',
            true_keys[0] + '.mult.y': true_keys[0] + '.y.9',
            true_keys[0] + '.mult.y.9': true_keys[0] + '.y.9',
            true_keys[0] + '.mult.x.11': true_keys[0] + '.x.9',
            true_keys[0] + '.mult.y.11': true_keys[0] + '.y.9',
            true_keys[0] + '.MathStuff.object': (true_keys[0] +
                                                '.object.13'),
            true_keys[0] + '.MathStuff.object.13': (true_keys[0] +
                                                   '.object.13'),
            true_keys[0] + '.MathStuff.__init__.self': (
                true_keys[0] + '.self.16'),
            true_keys[0] + '.MathStuff.__init__.self.16': (
                true_keys[0] + '.self.16'),
            true_keys[0] + '.MathStuff.__init__.algebra': (
                true_keys[0] + '.algebra.16'),
            true_keys[0] + '.MathStuff.__init__.algebra.16': (
                true_keys[0] + '.algebra.16'),

            true_keys[0] + '.MathStuff.get_vars.self': (
                true_keys[0] + '.self.20'),
            true_keys[0] + '.MathStuff.get_vars.self.20': (
                true_keys[0] + '.self.20'),
            true_keys[0] + '.MathStuff.get_vars.self.vars': (
                true_keys[0] + '.self.vars.21'),
            true_keys[0] + '.MathStuff.get_vars.self.vars.21': (
                true_keys[0] + '.self.vars.21'),

            true_keys[0] + '.MathStuff.plug_in_vars.self': (
                true_keys[0] + '.self.23'),
            true_keys[0] + '.MathStuff.plug_in_vars.self.23': (
                true_keys[0] + '.self.23'),

            true_keys[0] + '.MathStuff.plug_in_vars.variable': (
                true_keys[0] + '.variable.23'),
            true_keys[0] + '.MathStuff.plug_in_vars.variable.23': (
                true_keys[0] + '.variable.23'),
            true_keys[0] + '.MathStuff.plug_in_vars.variable.25': (
                true_keys[0] + '.variable.23'),

            true_keys[0] + '.MathStuff.plug_in_vars.number': (
                true_keys[0] + '.number.23'),
            true_keys[0] + '.MathStuff.plug_in_vars.number.23': (
                true_keys[0] + '.number.23'),
            true_keys[0] + '.MathStuff.plug_in_vars.number.26': (
                true_keys[0] + '.number.23'),

            true_keys[0] + '.MathStuff.plug_in_vars.i': (
                true_keys[0] + '.i.24'),
            true_keys[0] + '.MathStuff.plug_in_vars.i.24': (
                true_keys[0] + '.i.24'),
            true_keys[0] + '.MathStuff.plug_in_vars.i.26': (
                true_keys[0] + '.i.24'),

            true_keys[0] + '.MathStuff.plug_in_vars.ch': (
                true_keys[0] + '.ch.24'),
            true_keys[0] + '.MathStuff.plug_in_vars.ch.24': (
                true_keys[0] + '.ch.24'),
            true_keys[0] + '.MathStuff.plug_in_vars.ch.25': (
                true_keys[0] + '.ch.24'),

            # TODO(theahura): Incorrect handling of functions, obj scope.
            # See issue 42, 43
            true_keys[0] + '.MathStuff.__init__.algebra.split': (
                true_keys[0] + '.algebra.split.18'),
            true_keys[0] + '.MathStuff.__init__.algebra.split.18': (
                true_keys[0] + '.algebra.split.18'),
            true_keys[0] + '.MathStuff.__init__.self.vars': (
                true_keys[0] + '.self.vars.18'),
            true_keys[0] + '.MathStuff.__init__.self.vars.18': (
                true_keys[0] + '.self.vars.18'),
            true_keys[0] + '.MathStuff.plug_in_vars.enumerate': (
                true_keys[0] + '.enumerate.24'),
            true_keys[0] + '.MathStuff.plug_in_vars.enumerate.24': (
                true_keys[0] + '.enumerate.24'),
            true_keys[0] + '.MathStuff.plug_in_vars.self.vars': (
                true_keys[0] + '.self.vars.24'),
            true_keys[0] + '.MathStuff.plug_in_vars.self.vars.24': (
                true_keys[0] + '.self.vars.24'),
            true_keys[0] + '.MathStuff.plug_in_vars.self.vars.26': (
                true_keys[0] + '.self.vars.24'),


        }

        self.assertDictEqual(true_vars, var)

        self.assertDictEqual(import_mod, {})
        self.assertDictEqual(import_from, {})

        true_calls = {
            'test_data.index_test_data.test1.algebra.split.18': {
                'caller': 'test_data.index_test_data.test1.MathStuff.__init__.18',
                'source': 'test_data.index_test_data.test1.MathStuff.__init__.algebra.split'
            },
            'test_data.index_test_data.test1.enumerate.24': {
                'caller': 'test_data.index_test_data.test1.MathStuff.plug_in_vars.24',
                'source': 'test_data.index_test_data.test1.MathStuff.plug_in_vars.enumerate'
            }
        }

        self.assertDictEqual(calls, true_calls)

        import_mod = project_index[true_keys[1]]['imported_modules']
        import_from = project_index[true_keys[1]]['imported_from']

        self.assertDictEqual(import_mod, {'test1': 'test1'})
        self.assertDictEqual(import_from, {'MathStuff': ('MathStuff', 'test1')})

        # Known bugs:
        #   Does not handle calls through object attributes.
        #   Does not handle calls from a file global scope.
        true_forest = [
            {
                'name': 'test_data.index_test_data.test1.MathStuff.__init__',
                'children': [{
                    'name': ('test_data.index_test_data.test1.MathStuff.'
                             '__init__.algebra.split'),
                    'children': []
                }]
            },
            {
                'name': 'test_data.index_test_data.test1.MathStuff.get_vars',
                'children': []
            },
            {
                'name': 'test_data.index_test_data.test1.add',
                'children': []
            },
            {
                'name': 'test_data.index_test_data.test1.MathStuff.plug_in_vars',
                'children': [{
                    'name': ('test_data.index_test_data.test1.MathStuff.'
                             'plug_in_vars.enumerate'),
                    'children': []
                }]
            }]

        self.assertItemsEqual(forest, true_forest)

if __name__ == '__main__':
    unittest.main()
