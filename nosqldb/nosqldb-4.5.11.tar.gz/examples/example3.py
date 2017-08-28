#!/usr/bin/python
# This example:
#     1. Creates a table
#     2. Writes data in it with Durability opts
#     3. Reads that data with Consistency opts
#     4. Drops the table

import logging
import sys

from nosqldb import ConsistencyException
from nosqldb import Durability
from nosqldb import DurabilityException
from nosqldb import Factory
from nosqldb import IllegalArgumentException
from nosqldb import ProxyConfig
from nosqldb import ReadOptions
from nosqldb import RequestTimeoutException
from nosqldb import Row
from nosqldb import StoreConfig
from nosqldb import WriteOptions
from nosqldb import ABSOLUTE
from nosqldb import ONDB_CONSISTENCY
from nosqldb import ONDB_DURABILITY
from nosqldb import ONDB_MASTER_SYNC
from nosqldb import ONDB_REPLICA_ACK
from nosqldb import ONDB_REPLICA_SYNC
from nosqldb import ONDB_TIMEOUT
from runtimeopts import add_runtime_params
from runtimeopts import proxy_host_port
from runtimeopts import store_host_port
from runtimeopts import store_name

# default store_name, store_host_port and proxy_host_port are
# defined in runtimeopts.py

nosqlLogger = logging.getLogger("nosqldb")

# set logging level to debug and log to stdout
def setup_logging():
    # turn on logging in the python driver in DEBUG level
    StoreConfig.change_log("DEBUG")
    # add it the stdout handler
    logger = logging.StreamHandler(sys.stdout)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('\t%(levelname)s - %(message)s')
    logger.setFormatter(formatter)
    nosqlLogger.addHandler(logger)


# configure and open the store
def open_store():
    kvstoreconfig = StoreConfig(store_name, [store_host_port])
    kvproxyconfig = ProxyConfig()
    return Factory.open(proxy_host_port, kvstoreconfig, kvproxyconfig)


# drop table statement
def do_drop_table(store):
    ### Drop the table if it exists it can be recreated
    try:
        ddl = """DROP TABLE IF EXISTS myTable"""
        store.execute_sync(ddl)
        nosqlLogger.debug("Table drop succeeded")
        store.refresh_tables()
    except IllegalArgumentException, iae:
        nosqlLogger.error("DDL failed.")
        nosqlLogger.error(iae.message)
        return


def do_create_table(store):
    ### Drop table if exists
    do_drop_table(store)

    ### Create a table
    try:
        ddl = """CREATE TABLE myTable (
            item STRING,
            description STRING,
            count INTEGER,
            percentage FLOAT,
            PRIMARY KEY (item)
        )"""
        store.execute_sync(ddl)
        nosqlLogger.debug("Table creation succeeded")
        store.refresh_tables()
    except IllegalArgumentException, iae:
        nosqlLogger.error("DDL failed.")
        nosqlLogger.error(iae.message)


def do_write_data(store):
    store.refresh_tables()
    row_d = {'item': 'bolts',
             'description': "Hex head, stainless",
             'count': 5,
             'percentage': 0.2173913}
    row = Row(row_d)

    ## Create the write options

    ## This Durability is the same as you get if using
    ## COMMIT_SYNC. We do it the long way here for illustrative
    ## and readability purposes.
    dur = Durability({ONDB_MASTER_SYNC: 'SYNC',
                      ONDB_REPLICA_SYNC: 'NO_SYNC',
                      ONDB_REPLICA_ACK: 'SIMPLE_MAJORITY'})

    wo = WriteOptions({ONDB_DURABILITY: dur,
                       ONDB_TIMEOUT: 600})
    try:
        store.put("myTable", row, wo)
        nosqlLogger.debug("Store write succeeded.")
    except IllegalArgumentException, iae:
        nosqlLogger.error("Could not write table.")
        nosqlLogger.error(iae.message)
    except DurabilityException, de:
        nosqlLogger.error("Could not write table. Durability failure.")
        nosqlLogger.error(de.message)
    except RequestTimeoutException, rte:
        nosqlLogger.error("Could not write table. Exceeded timeout.")
        nosqlLogger.error(rte.message)


def display_row(row):
    try:
            print "Retrieved row:"
            print "\tItem: %s" % row['item']
            print "\tDescription: %s" % row['description']
            print "\tCount: %s" % row['count']
            print "\tPercentage: %s" % row['percentage']
            print "\n"
    except KeyError, ke:
        nosqlLogger.error("Row display failed. Bad key: %s" % ke.message)


def do_read_data(store):
    ## Create the simple consistency guarantee to use for this
    ## store read.
    ro = ReadOptions({ONDB_CONSISTENCY: ABSOLUTE,
                      ONDB_TIMEOUT: 600})
    try:
        primary_key_d = {"item": "bolts"}
        row = store.get("myTable", primary_key_d, ro)
        if not row:
            nosqlLogger.debug("Row retrieval failed")
        else:
            nosqlLogger.debug("Row retrieval succeeded.")
            display_row(row)
    except IllegalArgumentException, iae:
        nosqlLogger.error("Row retrieval failed.")
        nosqlLogger.error(iae.message)
        return
    except ConsistencyException, ce:
        nosqlLogger.error("Row retrieval failed due to Consistency.")
        nosqlLogger.error(ce.message)
    except RequestTimeoutException, rte:
        nosqlLogger.error("Row retrieval failed, exceeded timeout value.")
        nosqlLogger.error(rte.message)


if __name__ == '__main__':

    add_runtime_params()
    setup_logging()
    store = open_store()
    do_create_table(store)
    do_write_data(store)
    do_read_data(store)
    do_drop_table(store)
    store.close()
