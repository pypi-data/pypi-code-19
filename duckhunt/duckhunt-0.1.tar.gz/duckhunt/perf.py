#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from duckhunt import *
from datetime import datetime
import pickle
import json
import time                                                

def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print ('{:10} {:20} {:f} [ms]'.format(
              args, method.__name__, (te-ts)*1000))
        return result

    return timed

@duckhunt
class PassengerD(object):
    a_str = str
    a_int = int
    a_list = list
    a_dict = dict
    a_tuple = tuple
    a_object = datetime


@duckhunt
class BomD(object):
    a_str = str
    a_int = int
    a_list = list
    a_dict = dict
    a_tuple = tuple
    a_object = datetime
    a_duckhunt = PassengerD

@duckhuntlight
class PassengerL(object):
    a_str = str
    a_int = int
    a_list = list
    a_dict = dict
    a_tuple = tuple
    a_object = datetime


@duckhuntlight
class BomL(object):
    a_str = str
    a_int = int
    a_list = list
    a_dict = dict
    a_tuple = tuple
    a_object = datetime
    a_duckhunt = PassengerL

class Passenger(object):
    def __init__(self):
        self.a_str = str()
        self.a_int = int()
        self.a_list = list()
        self.a_dict = dict()
        self.a_tuple = tuple()
        self.a_object = datetime


class Bom(object):
    def __init__(self):
        self.a_str = str()
        self.a_int = int()
        self.a_list = list()
        self.a_dict = dict()
        self.a_tuple = tuple()
        self.a_object = datetime
        self.a_duckhunt = Passenger()


@timeit
def run_class(iterations):
    for i in xrange(iterations):
        p = Passenger()
        b = Bom()
        p.a_str = 'Pax Thomaç'

        b.a_str = '2344-cece-455'
        b.a_list = ['abc', 123, p]
        b.a_dict['key'] = 'value'
        b.a_tuple = (1, 2)
        b.a_object = datetime(1982, 1, 30  , 8, 30)
        b.a_duckhunt = p

@timeit
def run_duckthunt(iterations):
    for i in xrange(iterations):
        p = PassengerD()
        b = BomD()
        p.a_str = 'Pax Thomaç'

        b.a_str = '2344-cece-455'
        b.a_list = ['abc', 123, p]
        b.a_dict = dict()
        b.a_dict['key'] = 'value'
        b.a_tuple = (1, 2)
        b.a_object = datetime(1982, 1, 30  , 8, 30)
        b.a_duckhunt = p


@timeit
def run_duckthuntlight(iterations):
    for i in xrange(iterations):
        p = PassengerL()
        b = BomL()
        p.a_str = 'Pax Thomaç'

        b.a_str = '2344-cece-455'
        b.a_list = ['abc', 123, p]
        b.a_dict = dict()
        b.a_dict['key'] = 'value'
        b.a_tuple = (1, 2)
        b.a_object = datetime(1982, 1, 30  , 8, 30)
        b.a_duckhunt = p


def run(iterations):
    run_class(iterations)
    run_duckthuntlight(iterations)
    run_duckthunt(iterations)

run(10)
print('-------')
run(100)
print('-------')
run(200)
print('-------')
run(1000)
print('-------')
run(10000)




