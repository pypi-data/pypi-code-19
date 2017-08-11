
import os, re, subprocess, time
from bl.dict import Dict

import logging
log = logging.getLogger(__name__)

class File(Dict):
    def __init__(self, fn=None, data=None, **args):
        if type(fn)==str: fn=fn.strip().replace('\\ ', ' ')
        Dict.__init__(self, fn=fn, data=data, **args)

    def __repr__(self):
        return "%s(fn=%r)" % (
            self.__class__.__name__, self.fn)

    def open(self):
        subprocess.call(['open', fn], shell=True)

    def read(self, mode='rb'):
        with open(self.fn, mode) as f:
            data = f.read()
        return data

    def dirpath(self):
        return os.path.dirname(os.path.abspath(self.fn))

    @property
    def path(self):
        return self.dirpath()

    def basename(self):
        return os.path.basename(self.fn)

    def make_basename(self, fn=None, ext=None):
        """make a filesystem-compliant basename for this file"""
        fb, oldext = os.path.splitext(os.path.basename(fn or self.fn))
        ext = ext or oldext.lower()
        fb = re.sub("&[^;]*?;", ' ', fb)                          # remove entities
        fb = re.sub("""['"\u2018\u2019\u201c\u201d]""", ' ', fb)  # remove quotes
        fb = re.sub("\W+", '-', fb).strip(' -')                   # non-word to hyphen, collapse multiple
        return ''.join([fb, ext])

    def ext(self):
        return os.path.splitext(self.fn)[-1]

    def relpath(self, dirpath=None):
        return os.path.relpath(self.fn, dirpath or self.dirpath()).replace('\\','/')

    def mimetype(self):
        from mimetypes import guess_type
        return guess_type(self.fn)[0]

    def tempfile(self, mode='wb', **args):
        "write the contents of the file to a tempfile and return the tempfile filename"
        tf = tempfile.NamedTemporaryFile(mode=mode)
        self.write(tf.name, mode=mode, **args)
        return tfn

    def write(self, fn=None, data=None, mode='wb', 
                max_tries=3):                   # sometimes there's a disk error on SSD, so try 3x
        def try_write(fd, outfn, tries=0):         
            try:
                if fd is None and os.path.exists(self.fn):
                    if 'b' in mode:
                        fd=self.read(mode='rb')
                    else:
                        fd=self.read(mode='r')
                f = open(outfn, mode)
                f.write(fd or b'')
                f.close()
            except: 
                if tries < max_tries:
                    time.sleep(.1)              # I found 0.1 s gives the disk time to recover. YMMV
                    try_write(fd, outfn, tries=tries+1)
                else:
                    raise
        outfn = fn or self.fn
        if not os.path.exists(os.path.dirname(outfn)):
            log.debug("creating directory: %s" % os.path.dirname(outfn))
            os.makedirs(os.path.dirname(outfn))
        try_write(data or self.data, outfn, tries=0)

    @classmethod
    def readable_size(C, size, suffix='B'):
        if size is None: return
        size = float(size)
        for unit in ['','K','M','G','T','P','E','Z']:
            if abs(size) < 1024.0:
                return "%3.1f %s%s" % (size, unit, suffix)
            size /= 1024.0
        return "%.1f %s%s" % (size, 'Y', suffix)

