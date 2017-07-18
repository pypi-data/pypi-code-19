# LICENSE
#
# This file is released in the Public Domain.
#
# In case of copyright claims you can use this license 
# to prove that intention is to have no copyright on this work and
# consider it to be in the Publc Domain.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" log module to set standard format of logging. """

from botlib.static import BOLD, RED, YELLOW, GREEN, BLUE, BLA, ENDC

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
format_large = "%(asctime)-8s %(module)10s.%(lineno)-4s %(message)-60s (%(threadName)s)"
format_source = "%(asctime)-8s %(message)-60s (%(module)s.%(lineno)s)"
format_time = "%(asctime)-8s %(message)s"
format_log = "%(message)s"

class DumpHandler(logging.StreamHandler):

    """ Logger that logs nothing. """

    def emit(self, record):
        pass

class Formatter(logging.Formatter):

    """ Formatter that add's color (yes!) to logging. """

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

    """ Formatter that strips coloring (even more yes!) from the Logger. """

    def format(self, record):
        target = str(record.msg)
        if not target:
            target = " "
        if target[0] in [">", "<", "!", "#", "^", "-", "&"]:
            target = target[2:]
        record.msg = target
        return logging.Formatter.format(self, record)

def cdir(path):
    """ create directory. """
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
    """ log a line on given level. """
    l = LEVELS.get(str(level).lower())
    logging.log(l, error)

def loglevel(level, logpath=""):
    """ set loglevel to provided level. logpath can be used to define the directory to log into. """
    from .space import cfg
    level = level.upper()
    logger = logging.getLogger("")
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    dhandler = DumpHandler()
    logger.setLevel(level)
    logger.addHandler(dhandler)
    if cfg.verbose:
        formatter = Formatter(format_log, datefmt=datefmt)
        ch = logging.StreamHandler()
        ch.propagate = False
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    else:
        formatter_clean = FormatterClean(format_time, datefmt=datefmt)
        filehandler = logging.handlers.TimedRotatingFileHandler(os.path.join(logpath or cfg.logdir, "bot.log"), 'midnight')
        filehandler.setLevel(level)
        filehandler.setFormatter(formatter_clean)
        logger.addHandler(filehandler)
    return logger
