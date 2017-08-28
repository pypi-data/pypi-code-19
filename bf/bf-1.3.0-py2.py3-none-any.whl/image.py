
import logging
log = logging.getLogger(__name__)

import math, os, shutil, sys, subprocess
from bl.file import File

class Image(File):

    def im(self, cmd, quiet=True, **params):
        args = [cmd]
        if quiet==True:
            args += ['-quiet']
        for key in params.keys():
            args += ['-'+key]
            if str(params[key]) != "":
                args += [str(params[key])]
        args += [self.fn]
        log.debug("%r" % args)
        o = subprocess.check_output(args).decode('utf8')
        return o.strip()

    def gm(self, cmd, **params):
        args = ['gm', cmd]
        for key in params.keys():
            args += ['-'+key]
            if str(params[key]) != "":
                args += [str(params[key])]
        args += [self.fn]
        log.debug("%r" % args)
        o = subprocess.check_output(args).decode('utf8')
        return o.strip()

    def mogrify(self, **params):
        return self.im('mogrify', **params)

    def identify(self, **params):
        return self.im('identify', **params)

    def convert(self, outfn=None, **params):
        args = ['convert', self.fn]
        if outfn is None: 
            outfn = self.fn
        for key in params.keys():
            args += ['-'+key, str(params[key])]
        args += [outfn]
        log.debug("%r" % args)
        if not os.path.exists(os.path.dirname(outfn)):
            os.makedirs(os.path.dirname(outfn))
        o = subprocess.check_output(args).decode('utf8')
        return o.strip()
