from logging import debug
import logging
from errno import EEXIST
from os import access, utime, W_OK, sep, makedirs
from os.path import isdir, dirname, abspath, join, exists


class fsref(object):
    """ A reference to a file that might not yet exist. """

    def __init__(self, path):
        apath = abspath(path)

        self.abspath = apath
        self.fragments = apath.split(sep)
        self.exists = exists(apath)
        self.dirname = dirname(apath)

    def read(self):
        nlines = 0
        with open(self.abspath, 'r') as f:
            for line in f:
                yield line
                nlines += 1

        debug("Read %(nlines)d lines from %(target)s", {
            'nlines':  nlines,
            'target': self.abspath,
        })

    def write(self, lines=[], mode='a'):
	"""
	Write lines to file pointed to by cursor, creating intermediary
	directories. Return True if the file did not exist before.

        write() behaves like the 'touch' command with default args.
	"""
	try:
	    makedirs(self.dirname)
	except OSError as exc:
	    if exc.errno == EEXIST and isdir(self.dirname):
		pass
	    else:
		raise

	existed_before = self.exists
        with open(self.abspath, mode) as f:
            utime(self.abspath, None)
            for l in lines:
                f.write(l + "\n")

        debug("Wrote %(nlines)d lines to %(dest)s (%(status)s)", {
            'nlines':  len(lines),
            'dest': self.abspath,
            'status': "rewrite" if existed_before else "new",
        })

        self.exists = True

	return not existed_before

