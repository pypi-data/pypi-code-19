#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 15 21:58:46 2017

@author: pydemia
"""


import numpy as np
import pandas as pd
import unipy as up
import unipy_db as udb

# %%

def getDB_normal(query):
    data = udb.from_MariaDB(query, h='windows.pydemia.org', port=3306, db='employees', u='mdb', p='mdb')
    return data


async def getDB_async(query):
    data = await udb.from_MariaDB(query, h='windows.pydemia.org', port=3306, db='employees', u='mdb', p='mdb')
    return data

# %%

def emp_no_gen(start, end, term):
    pre, nxt = start, start + term -1
    yield pre, nxt
    while nxt < end:
        pre, nxt = nxt, nxt + term
        yield pre+1, nxt

# %%
queryStr = """
SELECT *
FROM employees.employees
WHERE EMP_NO BETWEEN {pre} AND {nxt}
;
"""

qList = [queryStr.format(pre=item[0], nxt=item[1]) for item in emp_no_gen(10001, 300000, 100000)]
qList = [queryStr.format(pre=10001, nxt=300001) for i in range(10)]

# %% Normal Loop
    
aList = [getDB_normal(q) for q in qList]

# %% Async but Loop

import asyncio

bList = [getDB_async(q) for q in qList]
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(bList))

# %% Multi-Processing

import multiprocessing

if __name__ == '__main__':
    pool = multiprocessing.pool.Pool(processes=4)
    response = pool.map(getDB_normal, qList, chunksize=1)
    
# %% Multi-Threading

import multiprocessing

if __name__ == '__main__':
    pool = multiprocessing.pool.ThreadPool(processes=4)
    response = pool.map(getDB_normal, qList, chunksize=1)

# %%

