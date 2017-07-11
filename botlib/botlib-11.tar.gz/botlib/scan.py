# botlib/scan.py
#
# Copyright 2016,2017 Bart Thate
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
# 
# * As the creator of this piece of software, Bart Thate, i disclaim all rights on the code contained in this software package.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

""" scan the home dir for madbot data dirs, dirs that contain a 'runtime' subdirectory. """

from .utils import locatedir, copydir

import os

def kopy(event):
    from .space import cfg, users
    if not users.allowed(event.origin, "OPER"):
        event.reply("you are not allowed to give the kopy command.")
        return
    if not event._parsed.args:
        event.reply("kopy <sourcedir>")
        return
    source = event._parsed.args[0]
    if not os.path.isdir(source):
        event.reply("%s is not a directory" % source)    
        return
    fns = copydir(source, cfg.workdir)
    event.reply("kopied %s files" % len(fns))

def scan(event):
    from .space import cfg, users
    if not users.allowed(event.origin, "OPER"):
        event.reply("you are not allowed to give the scan command.")
        return
    homedir = os.path.expanduser("~")
    cfg.workdirs = list(locatedir(homedir, 'runtime'))
    event.reply("using %s work directories." % len(cfg.workdirs))
