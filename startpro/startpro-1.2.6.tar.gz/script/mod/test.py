# encoding: utf8

"""
Created on 2016.01.13

@author: ZoeAllen
"""
from startpro.core.process import Process

print('import mod.test.py')


class Test(Process):
    name = 'hi.inner'

    def __init__(self):
        print('init hi.inner')

    def run(self, **kwargvs):
        print('check')
        print('run', kwargvs)

    def start(self):
        print('start')


class T2(Test):
    name = 'hi.test'

    def __init__(self):
        Test.__init__(self)
        print('init T2')


class T3(Process):

    def __init__(self):
        print('init T3')