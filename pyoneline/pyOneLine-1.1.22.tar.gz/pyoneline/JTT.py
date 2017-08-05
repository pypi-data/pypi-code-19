#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 15 10:56:21 2017

@author: zhoumingzhen
"""
import multiprocessing as mp
import fileinput as fi
import json


def __jsonOb(json0):
    try:
        if type(json0) == str:
            json0 = json.loads(json0)
        json_item = list(zip(json0.keys(),json0.values()))
        return json_item
    except:
        pass


def JTT(json1):
    #json1 as json_path <=> [{"a":1,"c":1},{"b":1}]
    #json1 as [{"a":1,"c":1},{"b":1}] <=> [[("a",1),("c",1)],[("b",1)]]
    #json1 as {"a":1,"b":1} <=> [(a,1),(b,1)]
    pool = mp.Pool(mp.cpu_count())
    if type(json1) == str:
        result = pool.map(__jsonOb, fi.FileInput(json1))
    if type(json1) == list or type(json1) == tuple:
        result = pool.map(__jsonOb, json1)
    if type(json1) == dict:
        return list(zip(json1.keys(),json1.values()))  
    pool.close()
    pool.join
    return result

    
if __name__ == '__main__':
    #print(JTT('./test_JX'))
    print(JTT([{"a":1},{"b":1}]))
    print(JTT({"a":1}))
    print(JTT([{"topic": "InstallVideoPlugin","message" : {"uid": 0 ,"time": 1493963414}}]))
    print(JTT({"topic": "InstallVideoPlugin","message" : {"uid": 0 ,"time": 1493963414}}))
