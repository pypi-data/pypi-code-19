# mod/scan.py
#
#

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
    