#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  4 21:34:16 2017

@author: Stephen.Z
"""


import multiprocessing as mp
import fileinput as fi

class MUL(object):
    def __init__(self, func, doc_path):
        self.func = func
        self.doc_path = doc_path
        self.qm()
        
    def qm(self):
        pool = mp.Pool(mp.cpu_count())
        pool.map(self.func, fi.FileInput(self.doc_path))
        pool.close()
        pool.join()
        
        


