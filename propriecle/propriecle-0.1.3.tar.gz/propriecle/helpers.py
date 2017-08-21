"""Mostly context agnostic helpers"""
import sys
import atexit
from threading import Event
import curses

FINISHED = Event()


def end_curse():
    """Clean up our curses environment, ignoring any
    problems  while doing so."""
    try:
        curses.endwin()
    except curses.error:
        pass


def problems(msg):
    """Rudimentary handling of problems"""
    end_curse()
    print("Problem: %s" % msg)
    FINISHED.set()
    sys.exit(1)


def do_write(data, dest):
    """Cleanly write a file out somewhere"""
    handle = open(dest, 'w')
    handle.write(data)
    handle.close()


def finish():
    """Clean up and signal that the end has arrived to
    our various Vault polling threads"""
    end_curse()
    FINISHED.set()


atexit.register(finish)
