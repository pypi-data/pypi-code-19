# -*- coding: utf-8 -*-
"""
Created on Thu Jan  5 20:55:26 2017

@author: Young Ju Kim
"""

import pandas as pd

import psycopg2 as pg
import sqlalchemy as sa
# import ibm_db_sa

from unipy.util.wrapper import time_profiler

__all__ = ['to_MariaDB']

@time_profiler
def to_MariaDB(DataFrame, db=None, table=None, h=None, port=3306, u=None, p=None,
            if_exists='append'):

    print('Using MariaDB')

    # DB Connection
    connStr = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'
    engine = sa.create_engine(connStr.format(u, p, h, str(port), db))

    # Get a DataFrame
    DataFrame.to_sql(con=engine, name=table, if_exists=if_exists,
                     index=False, chunksize=None)

