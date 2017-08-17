import os
import sys
import time
import traceback
from pprint import pprint

from termcolor import cprint as _cprint


class Moleskin:
    def __init__(self, debug=True, file=None):
        self.is_debug = debug
        self.log_filename = file
        if self.log_filename:
            path, file = os.path.split(self.log_filename)
            try:
                os.makedirs(path)
            except FileExistsError:
                pass

        self.tic = None

    def start(self):
        self.tic = time.time()

    def split(self, debug=False, time_format=":.4f"):
        if self.tic is None:
            raise Exception('Need to start the timer first.')
        toc = time.time()
        if debug:
            self.debug("Split Time {}s".format(toc - self.tic))
        else:
            self.grey("Lap Time:", end=' ')
            self.green(("{" + time_format + "}s").format(toc - self.tic))
        self.tic = toc

    def p(self, *args, **kwargs):
        self.print(*args, **kwargs)

    def print(self, *args, **kwargs):
        """use stdout.flush to allow streaming to file when used by IPython. IPython doesn't have -u option."""
        if self.log_filename and 'file' not in kwargs:
            with open(self.log_filename, 'a+') as logfile:
                print(*args, **kwargs, file=logfile)
        print(*args, **kwargs)
        sys.stdout.flush()

    def cp(self, *args, **kwargs):
        self.cprint(*args, **kwargs)

    def cprint(self, *args, sep=' ', color='white', **kwargs):
        """use stdout.flush to allow streaming to file when used by IPython. IPython doesn't have -u option."""
        if self.log_filename and 'file' not in kwargs:
            with open(self.log_filename, 'a+') as logfile:
                _cprint(sep.join([str(a) for a in args]), color, **kwargs, file=logfile)
        _cprint(sep.join([str(a) for a in args]), color, **kwargs)
        sys.stdout.flush()

    def pp(self, *args, **kwargs):
        self.pprint(*args, **kwargs)

    def pprint(self, *args, **kwargs):
        if self.log_filename and 'file' not in kwargs:
            with open(self.log_filename, 'a+') as logfile:
                pprint(*args, **kwargs, file=logfile)
        pprint(*args, **kwargs)
        sys.stdout.flush()

    def log(self, *args, **kwargs):
        """use stdout.flush to allow streaming to file when used by IPython. IPython doesn't have -u option."""
        self.print(*args, **kwargs)

    # TODO: take a look at https://gist.github.com/FredLoney/5454553
    def debug(self, *args, **kwargs):
        # DONE: current call stack instead of last traceback instead of.
        if self.is_debug:
            stacks = traceback.extract_stack()
            last_caller = stacks[-2]
            path = last_caller.filename.split('/')
            if len(path) >= 2:
                self.white(path[-2], end='/')
            if len(path) >= 1:
                self.green(path[-1], end=' ')
            self.white('L', end='')
            self.red('{}'.format(last_caller.lineno), end='')
            self.print(': ', end='')
            self.grey(last_caller.line)
            self.print(*args, **kwargs)

    def refresh(self, *args, **kwargs):
        """allow keyword override of end='\r', so that only last print refreshes the console."""
        # to prevent from creating new line
        # default new end to single space.
        if 'end' not in kwargs:
            kwargs['end'] = ' '
        self.print('\r', *args, **kwargs)

    def info(self, *args, **kwargs):
        self.cprint(*args, color='blue', **kwargs)

    def error(self, *args, sep='', **kwargs):
        self.cprint(*args, color='red', **kwargs)

    def warn(self, *args, **kwargs):
        self.cprint(*args, color='yellow', **kwargs)

    def highlight(self, *args, **kwargs):
        self.cprint(*args, color='green', **kwargs)

    def green(self, *args, **kwargs):
        self.cprint(*args, color='green', **kwargs)

    def grey(self, *args, **kwargs):
        self.cprint(*args, color='grey', **kwargs)

    def gray(self, *args, **kwargs):
        self.grey(*args, **kwargs)

    def red(self, *args, **kwargs):
        self.cprint(*args, color='red', **kwargs)

    def yellow(self, *args, **kwargs):
        self.cprint(*args, color='yellow', **kwargs)

    def blue(self, *args, **kwargs):
        self.cprint(*args, color='blue', **kwargs)

    def magenta(self, *args, **kwargs):
        self.cprint(*args, color='magenta', **kwargs)

    def cyan(self, *args, **kwargs):
        self.cprint(*args, color='cyan', **kwargs)

    def white(self, *args, **kwargs):
        self.cprint(*args, color='white', **kwargs)

    # def assert(self, statement, warning):
    #     if not statement:
    #         self.error(warning)
    #

    def raise_(self, exception, *args, **kwargs):
        self.error(*args, **kwargs)
        raise exception
