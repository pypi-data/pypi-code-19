# BOTLIB - Framework to program bots.
#
# Copyright (C) 2017 by Bart Thate <bthate@dds.nl>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES 
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF 
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE 
# FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY 
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

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
