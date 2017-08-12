import os
import csv

import pkg_resources

class Translator(object):
    # only works for strings
    def _flatten(self, l):
        if len(l) > 0:
            return self._flatten(l[0]) + (self._flatten(l[1:]) if len(l) > 1 else []) if type(l) is list else [l]
        else:
            return []

    def _read_translator(self):

        csvfile = open(self.translator_file, 'rb')

        spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')

        header = spamreader.next()

        types = [ item for item in header if item != '' ]

        translator  = {}
        idxes       = {}
        for key in types:
            idxes[key]      = header.index(key)
            translator[key] = []

        for row in spamreader:
            for key in idxes.keys():
                translator[key] += [ row[ idxes[key] ] ]

        translator['TUV']       = [ x.replace(' ', '') for x in translator['TUV'] ]

        # other_names splitting
        for i, x in enumerate(translator['BOXMOX']):
            translator['BOXMOX'][i] = translator['BOXMOX'][i].split(',')

        return translator, types

    def translate(self, vars, xfrom, to):
        '''
        Translate keys between BOXMOX, MCM and TUV
        '''
        if (isinstance(vars, str)):
            vars = [ vars ]

        if xfrom not in self.translator.keys():
            print("'From' key <" + xfrom + "> does not exist.")
            return []
        if to not in self.translator.keys():
            print("'To' key <" + to + "> does not exist.")
            return []

        if xfrom == 'TUV':
            vars = [ x.replace(' ', '') for x in vars ]

        # test for identical species, account for possibility of lists as 'y'
        def identity(x, y):
            if isinstance(y, str):
                return x == y
            else:
                return any( [ x == l for l in y ] )

        result = {}
        for var in vars:
            idxes       = [ i for i,x in enumerate(self.translator[xfrom]) if identity(var, x) ]
            values      = [ self.translator[to][i] for i in idxes if self.translator[to][i] != '' ]
            values      = self._flatten(values)
            values      = list(set(values))
            # if there is a true one-to-one identity - make it a string
            if len(values) == 1:
                values = values[0]
            result[var] = values

        # if vars is a single variable - reduce to list
        if len(vars) == 1:
            result = result[vars[0]]

        return result

    def __init__(self, translator_file = None):
        self.translator_file = translator_file
        if self.translator_file is None:
            data_dir        = pkg_resources.resource_filename(__name__, 'data')
            self.translator_file = os.path.join(data_dir, 'equivalence.csv')

        self.translator, self.types = self._read_translator()
