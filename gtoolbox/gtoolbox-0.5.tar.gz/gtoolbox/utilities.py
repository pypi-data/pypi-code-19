#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import subprocess
from contextlib import contextmanager
__author__ = 'Kandit'
import logging
import sys
from collections import namedtuple
import atexit

def Region(latmin,latmax,lonmin,lonmax):
    Reg = namedtuple("Region",["latrange","lonrange"])
    Latrange = namedtuple("Latrange",["min","max"])
    Lonrange = namedtuple("Lonrange",["min","max"])
    Reg.contains= lambda self,lat,lon: True if latmin<=lat <=latmax and lonmin<=lon <=lonmax else False
    return Reg(Latrange(latmin,latmax),Lonrange(lonmin,lonmax))



class Region():
    def __init__(self,latmin,latmax,lonmin,lonmax,name=""):
        pass


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def getPrint(color):
        def myprint(st):
            print color + st + bcolors.ENDC
        return myprint








class DFH(object):
    def __init__(self, done_file_name, key):


        touch(done_file_name)
        self.done_file_name = done_file_name
        self.__donelist, self.__donefile = self.__init_done(done_file_name, key,4000)



    def __init_done(self,done_file_name, key, maxlen):
        with open(done_file_name, "rw+") as donefl:

            donelist_raw = sorted(donefl.readlines(),key=key)

            l = len(donelist_raw)
            if l > maxlen + 500:
                newlist = donelist_raw[(l - maxlen):]

                donefl.seek(0)
                donefl.truncate()
                donefl.seek(0)
                donefl.writelines(newlist)
        newlist = set(map(lambda s: s.strip(), donelist_raw))
        return newlist, open(done_file_name, "a")


    def sort_log(self,key = lambda x:x,reverse=False):

        donelist_raw = open(self.done_file_name, "r").readlines()
        donelist_raw = sorted(donelist_raw,key=key)
        newdonefl = open(self.done_file_name, "w")
        newdonefl.writelines(donelist_raw)
        newdonefl.close()

    def mark_done(self, item):
        self.__donefile.write(item + "\n")
        self.__donefile.flush()


    def is_done(self, url):
        return url in self.__donelist


    def filter_done(self, itemlst):
        return [u for u in itemlst if not self.is_done(u)]


@contextmanager
def working_directory(path):
    prev_cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def init_logger(logfile = os.path.splitext(os.path.normpath(sys.argv[0]))[0] +".log"):

    logfile = touch(logfile)
    logger = logging.getLogger(os.path.splitext(os.path.basename(os.path.normpath(sys.argv[0])))[0])
    print os.path.splitext(os.path.basename(os.path.normpath(sys.argv[0])))[0]
    logger.errFlag = False

    def myerrorfun(x):
        logger.errFlag = True
        logger.native_error(x)

    logger.native_error = logger.error
    logger.error = myerrorfun

    file_handler = logging.FileHandler(logfile)
    stream_handler = logging.StreamHandler()  # stt err
    formatter = logging.Formatter('%(asctime)s  %(message)s')
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    logger.setLevel(logging.DEBUG)

    return logger


def du(path):
    """disk usage in human readable format (e.g. '2,1GB')"""
    try:
        bytess = subprocess.check_output(['du', '-s', path]).split()[0].decode('utf-8')
    except:
        bytess = "NaN"
    return bytess


def touch(fname, times=None):
    if not os.path.exists(fname):
        with open(fname, 'a'):
            os.utime(fname, times)
    return fname


class Multierror(Exception):
    errors = []

    def __init__(self, *args, **kwargs):
        super(Multierror, self).__init__(*args, **kwargs)


    def addError(self, ex):
        self.errors.append(ex)

    def addErrors(self, exs):
        self.errors.extend(exs)



def run_async(threadname):
    def run_in_thread(func):
        """
            run_async(func)
                function decorator, intended to make "func" run in a separate
                thread (asynchronously).
                Returns the created Thread object

                E.g.:
                @run_async
                def task1():
                    do_something

                @run_async
                def task2():
                    do_something_too

                t1 = task1()
                t2 = task2()
                ...
                t1.join()
                t2.join()
        """
        from threading import Thread
        from functools import wraps

        @wraps(func)
        def async_func(*args, **kwargs):
            func_hl = Thread(target = func, args = args, kwargs = kwargs,name = threadname)
            func_hl.start()
            return func_hl

    return run_in_thread


