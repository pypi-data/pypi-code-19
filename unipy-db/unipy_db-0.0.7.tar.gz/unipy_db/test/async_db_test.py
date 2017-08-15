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

async def getDB(query):
    data = await udb.from_MariaDB(query, h='windows.pydemia.org', port=3306, db='employees', u='mdb', p='mdb')
    return data


# %%

def emp_no_gen(start, end, term):
    pre, nxt = start, start + term -1
    yield pre, nxt
    while nxt < end:
        pre, nxt = nxt, nxt + term
        yield pre+1, nxt

noList = np.arange(10001, 100000, 10000).tolist()
geList = list(emp_no_gen(10001, 100000, 10000))

# %%
    
queryStr = """
SELECT FIRST_NAME, LAST_NAME, DEPARTMENT_ID
FROM EMPLOYEES.EMPLOYEES
WHERE EMP_NO BETWEEN {pre} AND {nxt}
;
"""


qList = [queryStr.format(pre=item[0], nxt=item[1]) for item in emp_no_gen(10001, 100000, 10000)]
aList = [getDB(q) for q in qList]

# %%

import asyncio

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(aList))


getDB(qList[0])

