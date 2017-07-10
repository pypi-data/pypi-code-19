# botlib/log.py
#
#

""" log module to set standard format of logging. """

from .static import *

import logging.handlers
import logging
import socket
import os

homedir = os.path.expanduser("~")
curdir = os.getcwd()

try:
    hostname = socket.getfqdn()
except:
    hostname = "localhost"

logdir = homedir + os.sep + ".botlog" + os.sep
logcurdir = curdir + os.sep + ".botlog" + os.sep

datefmt = '%H:%M:%S'
format_large = "%(asctime)-8s %(message)-8s %(module)s.%(lineno)s %(threadName)-10s"
format_source = "%(message)-8s %(module)s.%(lineno)-15s"
format_time = "%(asctime)-8s %(message)s"
format = "%(message)s"

class DumpHandler(logging.StreamHandler):

    def emit(self, *args, **kwargs):
        pass

class Formatter(logging.Formatter):

    def format(self, record):
        target = str(record.msg)
        if not target:
            target = " "
        if target[0] in [">", ]:
            target = "%s%s%s%s%s" % (BOLD, YELLOW, target[0], ENDC, target[1:])
        elif target[0] in ["<", ]:
            target = "%s%s%s%s%s" % (BOLD, GREEN, target[0], ENDC, target[1:])
        elif target[0] in ["!", ]:
            target = "%s%s%s%s%s" % (BOLD, BLA, target[0], ENDC, target[1:])
        elif target[0] in ["#", ]:
            target = "%s%s%s%s" % (RED, target[0], ENDC, target[1:])
        elif target[0] in ["^", ]:
            target = "%s%s%s%s%s" % (BOLD, BLUE, target[0], ENDC, target[1:])
        elif target[0] in ["-", ]:
            target = "%s%s%s%s" % (BOLD, target[0], ENDC, target[1:])
        elif target[0] in ["&", ]:
            target = "%s%s%s%s" % (RED, target[0], ENDC, target[1:])
        record.msg = target
        return logging.Formatter.format(self, record)

class FormatterClean(logging.Formatter):

    def format(self, record):
        target = str(record.msg)
        if not target:
            target = " "
        if target[0] in [">", "<", "!", "#", "^", "-", "&"]:
            target = target[2:]
        record.msg = target
        return logging.Formatter.format(self, record)

def cdir(path):
    res = "" 
    for p in path.split(os.sep):
        res += "%s%s" % (p, os.sep)
        padje = os.path.abspath(os.path.normpath(res))
        try:
            os.mkdir(padje)
        except (IsADirectoryError, NotADirectoryError, FileExistsError):
            pass
    return True

def log(level, error):
    l = LEVELS.get(str(level).lower())
    logging.log(l, error)

def loglevel(level, dir=""):
    from .space import cfg
    level = level.upper()
    if dir:
        global logdir
        logdir = dir
    if not os.path.exists(logdir):
        cdir(logdir)
    logger = logging.getLogger("")
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    dhandler = DumpHandler()
    logger.propagate = False
    logger.setLevel(level)
    logger.addHandler(dhandler)        
    if cfg.verbose:
        formatter = Formatter(format_time, datefmt=datefmt)
        ch = logging.StreamHandler()
        ch.propagate = False
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    else:
        formatter_clean = FormatterClean(format, datefmt=datefmt)
        filehandler = logging.handlers.TimedRotatingFileHandler(os.path.join(logdir, "bot.log"), 'midnight')
        filehandler.setLevel(level)
        filehandler.setFormatter(formatter_clean)
        logger.addHandler(filehandler)
    return logger