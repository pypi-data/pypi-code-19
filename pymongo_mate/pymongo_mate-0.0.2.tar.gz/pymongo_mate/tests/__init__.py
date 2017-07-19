#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import pymongo
import mongomock

py_ver = "%s%s" % (sys.version_info.major, sys.version_info.minor) 
col_name = "test_col_py%s" % py_ver

try:
    # Create Client
    # local
    #     client = pymongo.MongoClient(
    #         "localhost", 27017, serverSelectionTimeoutMS=1000)

    # mlab cloud
    url = "mongodb://{dbuser}:{dbpassword}@ds113063.mlab.com:13063/devtest".\
        format(dbuser="admin", dbpassword="&2z7#tMH6BJt")
    client = pymongo.MongoClient(url, serverSelectionTimeoutMS=1000)

    # Use Database
    db = client.__getattr__("devtest")

    # Connect to Collection
    col_real = db.__getattr__(col_name)
    col_real.drop()
except Exception as e:
    col_real = None

# Create Mongomock Client
col_mock = mongomock.MongoClient().devtest.__getattr__(col_name)
col_mock.drop()
