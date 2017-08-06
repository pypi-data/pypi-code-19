#!/usr/bin/env python
#
# Flattened nested dict
# Copyright (C) 2017 Larroque Stephen
#
# Licensed under the MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import sys

PY3 = (sys.version_info >= (3,0))

class fdictmin2(dict):
    '''Flattened nested dict, all items are settable and gettable through ['item1']['item2'] standard form or ['item1/item2'] internal form.
    This allows to replace the internal dict with any on-disk storage system like a shelve's shelf (great for huge nested dicts that cannot fit into memory).
    Main limitation: an entry can be both a singleton and a nested fdict, and there is no way to tell what is what, no error will be shown, the singleton will always be returned.
    '''
    def __init__(self, d=None, rootpath='', delimiter='/', *args):
        if d:
            self.d = d
        else:
            self.d = {}
        self.rootpath = rootpath
        self.delimiter = delimiter
        self._py3compat()
        #return dict.__init__(self, *args)

    def _py3compat(self):
        if PY3:
            # Py3
            self._viewkeys = self.d.keys
            self._viewvalues = self.d.values
            self._viewitems = self.d.items
        else:
            # Py2
            if getattr(self.d, "viewvalues", None):
                # Py2.7
                self._viewkeys = self.d.viewkeys
                self._viewvalues = self.d.viewvalues
                self._viewitems = self.d.viewitems
            else:
                # Py2.6
                self._viewkeys = self.d.iterkeys
                self._viewvalues = self.d.itervalues
                self._viewitems = self.d.iteritems

    def _buildpath(self, key):
        return self.rootpath+self.delimiter+key if self.rootpath else key

    def __getitem__(self, key):
        # Node or leaf?
        if key in self.d: # Leaf: return the value
            return self.d.__getitem__(key)
        else: # Node: return a new full fdict based on the old one but with a different rootpath to limit the results by default
            return fdict(d=self.d, rootpath=self._buildpath(key))
        #return dict.__getitem__(self, key)

    def __setitem__(self, key, value):
        #fullkey = self._buildpath(key)
        #if fullkey in self.d and :
        #    raise ValueError('Conflict detected: the following key is both a singleton and a nested dict: %s' % fullkey)
        self.d.__setitem__(self._buildpath(key), value)
        #dict.__setitem__(self, key, value)

    #def addchild(self, key, value=None):
    #    self.d[self._buildpath(key)] = value

    def viewkeys(self):
        if not self.rootpath:
            return self._viewkeys()
        else:
            pattern = self.rootpath+self.delimiter
            lpattern = len(pattern)
            return (k[lpattern:] for k in self._viewkeys() if k.startswith(pattern))

    def viewitems(self):
        # Filter items to keep only the ones below the rootpath level
        if not self.rootpath:
            return self._viewitems()
        else:
            pattern = self.rootpath+self.delimiter
            lpattern = len(pattern)
            return ((k[lpattern:], v) for k,v in self._viewitems() if k.startswith(pattern))

    def viewvalues(self):
        if not self.rootpath:
            return self._viewvalues()
        else:
            pattern = self.rootpath+self.delimiter
            lpattern = len(pattern)
            return (v for k,v in self._viewitems() if k.startswith(pattern))

    iterkeys = viewkeys
    itervalues = viewvalues
    iteritems = viewitems
    if PY3:
        keys = viewkeys
        values = viewvalues
        items = viewitems
    else:
        def keys(self):
            return list(self.viewkeys())
        def values(self):
            return list(self.viewvalues())
        def items(self):
            return list(self.viewitems())

    def update(self, d2):
        return self.d.update(d2.d)

    def __eq__(self, d2):
        return (self.d == d2)

    def __repr__(self):
        # Filter the items if there is a rootpath and return as a new fdict
        if self.rootpath:
            return repr(fdict(d=dict(self.items())))
        else:
            try:
                return self.d.__repr__()
            except AttributeError as exc:
                return repr(dict(self.items()))

    def __str__(self):
        if self.rootpath:
            return str(fdict(d=dict(self.items())))
        else:
            try:
                return self.d.__str__()
            except AttributeError as exc:
                return str(dict(self.items()))

    def to_dict(self):
        return dict(self.items())
