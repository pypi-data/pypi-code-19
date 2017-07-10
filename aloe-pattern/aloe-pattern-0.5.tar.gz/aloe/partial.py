import re

from logging import debug
from errno import ENOENT
from files import fsref
from os import getcwd
from os.path import join

import cache


def shorthand(partialbasename):
    start = 1 if partialbasename[0] == '_' else 0
    end = -5 if partialbasename.endswith('.scss') else None

    return partialbasename[start:end]

def qualified(dn, sh):
    return join(dn, '_{}.scss'.format(shorthand(sh)))

def importref(cursor):
    if cursor.abspath.endswith(Rind.filename):
        return '{}/_'.format(cursor.fragments[-2])

    return shorthand(cursor.fragments[-1])

def refresh():
    nfiles = 0
    for path, deps in cache.dump():
        ref = fsref(path)
        ref.write(['@import "{}";'.format(d) for d in deps], 'w')
        nfiles += 1

    debug("Wrote %d files", nfiles)


class Rind(fsref):
    """ SCSS partial that organizes dependencies according to Aloe. """

    filename = '__.scss'
    boundary = getcwd()
    importpattern = re.compile('^@import "([^"]+)";')

    def __init__(self, hostdir):
        super(Rind, self).__init__(join(hostdir, self.filename))

        # Read existing imports to persist user code.
        if not cache.cached(self.abspath) and self.exists:
            for line in self.read():
                m = self.importpattern.match(line)
                if m is not None and m.group(1):
                    impref = m.group(1)
                    group = 1 if impref.endswith('_') else 0
                    cache.store(self.abspath, group, impref)

        # Recursively discover build partials leading up to file boundary,
        # but only if this build partial does not yet exist.
        if not self.exists and self.dirname != self.boundary:
            Rind(join(self.dirname, '..')).link(self)

    def link(self, cursor):
        group = 1 if cursor.abspath.endswith(self.filename) else 0
        cache.store(self.abspath, group, importref(cursor))

    def unlink(self, cursor):
        cache.delete(self.abspath, importref(cursor))
