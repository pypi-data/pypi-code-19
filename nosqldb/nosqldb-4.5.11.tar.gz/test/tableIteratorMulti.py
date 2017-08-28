#
#  This file is part of Oracle NoSQL Database
#  Copyright (C) 2014, 2017 Oracle and/or its affiliates.  All rights reserved.
#
# If you have received this file as part of Oracle NoSQL Database the
# following applies to the work as a whole:
#
#   Oracle NoSQL Database server software is free software: you can
#   redistribute it and/or modify it under the terms of the GNU Affero
#   General Public License as published by the Free Software Foundation,
#   version 3.
#
#   Oracle NoSQL Database is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Affero General Public License for more details.
#
# If you have received this file as part of Oracle NoSQL Database Client or
# distributed separately the following applies:
#
#   Oracle NoSQL Database client software is free software: you can
#   redistribute it and/or modify it under the terms of the Apache License
#   as published by the Apache Software Foundation, version 2.0.
#
# You should have received a copy of the GNU Affero General Public License
# and/or the Apache License in the LICENSE file along with Oracle NoSQL
# Database client or server distribution.  If not, see
# <http://www.gnu.org/licenses/>
# or
# <http://www.apache.org/licenses/LICENSE-2.0>.
#
# An active Oracle commercial licensing agreement for this product supersedes
# these licenses and in such case the license notices, but not the copyright
# notice, may be removed by you in connection with your distribution that is
# in accordance with the commercial licensing terms.
#
# For more information please contact:
#
# berkeleydb-info_us@oracle.com
#
import time
import unittest

from nosqldb import Factory
from nosqldb import IllegalArgumentException
from nosqldb import Row
from nosqldb import TimeToLive
from nosqldb import ONDB_DAYS
from nosqldb import ONDB_TIMEUNIT
from nosqldb import ONDB_TTL_TIMEUNIT
from nosqldb import ONDB_TTL_VALUE
from testSetup import add_runtime_params
from testSetup import get_kvproxy_config
from testSetup import get_kvstore_config
from testSetup import get_store
from testSetup import host_port
from testSetup import set_security
from testSetup import table_name


class TestTableIteratorMulti(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._store = get_store()
        cls._store.execute_sync("DROP TABLE IF EXISTS " +
            table_name + "testTable.childTable.grandChildTable")
        cls._store.execute_sync("DROP TABLE IF EXISTS " +
            table_name + "testTable.childTable")
        cls._store.refresh_tables()
        time.sleep(1)
        cls._store.execute_sync("DROP TABLE IF EXISTS " +
            table_name + "testTable")
        cls._store.refresh_tables()
        cls._store.execute_sync(
            "CREATE TABLE IF NOT EXISTS " + table_name + "testTable (" +
            "shardKey INTEGER, id INTEGER, s STRING, " +
            "PRIMARY KEY (SHARD(shardKey), id) )")
        cls._store.execute_sync(
            "CREATE TABLE IF NOT EXISTS " + table_name +
            "testTable.childTable (" +
            "cid INTEGER, phoneCat ENUM (Home, Office, Cell, Other), " +
            "phone STRING, PRIMARY KEY (cid))")
        cls._store.execute_sync(
            "CREATE TABLE IF NOT EXISTS " + table_name +
            "testTable.childTable.grandChildTable (" +
            "bid INTEGER, billAddress STRING, billAmount DOUBLE," +
            "PRIMARY KEY(bid))")
        cls._store.refresh_tables()
        shardkeys = list(range(50))
        ids = list(range(50))
        ss = ['John', 'Mike', 'Jen', 'Rossy']
        phoneCats = ['Office', 'Other', 'Home', 'Cell']
        phones = ['123-1234', '555-2375', '111-0987', '1010-2442']
        billAddresses = ['123 First Ave', '301 Lake Rd', '789 Grand St',
            '555 Fourth St']
        billAmounts = [399.99, 149.99, 129.99, 269.99]
        ttl = TimeToLive({ONDB_TTL_VALUE: 5,
                          ONDB_TTL_TIMEUNIT: {ONDB_TIMEUNIT: ONDB_DAYS}})
        global expect_expiration
        expect_expiration = ttl.calculate_expiration(time.time() * 1000)
        for sk in shardkeys:
            for i in ids:
                row = Row({
                    'id': i,
                    's': ss[i % len(ss)] + str((i * sk) % len(ss)),
                    'shardKey': sk})
                row.set_timetolive(ttl)
                cls._store.put(table_name + "testTable", row)
                row2 = Row({
                    'id': i,
                    'shardKey': sk,
                    'cid': 0,
                    'phoneCat': phoneCats[i % len(phoneCats)],
                    'phone': phones[i % len(phones)]})
                cls._store.put(table_name + "testTable.childTable", row2)
                row3 = Row({
                    'id': i,
                    'shardKey': sk,
                    'cid': 0,
                    'bid': 0,
                    'billAddress': billAddresses[i % len(billAddresses)],
                    'billAmount': billAmounts[i % len(billAmounts)]})
                cls._store.put(
                    table_name + "testTable.childTable.grandChildTable",
                    row3)

    @classmethod
    def tearDownClass(cls):
        cls._store.execute_sync("DROP TABLE IF EXISTS " +
            table_name + "testTable.childTable.grandChildTable")
        cls._store.execute_sync("DROP TABLE IF EXISTS " +
            table_name + "testTable.childTable")
        cls._store.execute_sync("DROP TABLE IF EXISTS " +
            table_name + "testTable")
        cls._store.refresh_tables()
        cls._store.close()

    def setUp(self):
        s_config = get_kvstore_config()
        p_config = get_kvproxy_config()
        set_security(s_config, p_config)
        s_config.set_max_results(25)
        s_config.set_request_timeout(100)
        self.store = Factory.open(host_port, s_config, p_config)
        self.table = table_name + "testTable"

    def tearDown(self):
        self.store.close()

    def testTableIteratorShardkeys(self):
        # Use 3 valid keys (complete shard keys, partial primary keys)
        keys = [{'shardKey': 0},{'shardKey': 1},{'shardKey': 2}]

        # iterate rows
        count = 0
        it = self.store.multi_key_table_iterator(self.table, keys, False)
        for i in it:
            count += 1
            # s is a non-key field, it will be present
            s = i.get('s')
            self.assertIsNotNone(s)
        self.assertEqual(count, 150)
        it.close()

        # iterate keys
        count = 0
        it = self.store.multi_key_table_iterator(self.table, keys, True)
        for i in it:
            count += 1
            # s is a non-key field, it won't be present
            s = i.get('s')
            self.assertIsNone(s)
        self.assertEqual(count, 150)
        it.close()

    def testTableIteratorNoShardKey(self):
        self.assertRaises(IllegalArgumentException,
                          self.store.multi_key_table_iterator,
                          self.table, [{'id': 0},{'shardKey': 1},
                                       {'shardKey': 2}], False)

    def testTableIteratorNoneKey(self):
        self.assertRaises(IllegalArgumentException,
                          self.store.multi_key_table_iterator,
                          self.table, [None,{'shardKey': 1},
                                       {'shardKey': 2}], True)

    def testTableIteratorRowsWithTTL(self):
        day_in_milliseconds = 24 * 60 * 60 * 1000
        keys = [{'shardKey': 8},{'shardKey': 17},{'shardKey': 32}]

        # iterate rows
        count = 0
        it = self.store.multi_key_table_iterator(self.table, keys, False)
        for i in it:
            actual_expiration = i.get_expiration()
            actual_expect_diff = actual_expiration - expect_expiration
            self.assertGreater(actual_expiration, 0)
            self.assertLess(actual_expect_diff, day_in_milliseconds)
            self.assertGreaterEqual(actual_expect_diff, 0)
            count += 1
        self.assertEqual(count, 150)
        it.close()

        # iterate keys
        count = 0
        it = self.store.multi_key_table_iterator(self.table, keys, True)
        for i in it:
            actual_expiration = i.get_expiration()
            actual_expect_diff = actual_expiration - expect_expiration
            self.assertGreater(actual_expiration, 0)
            self.assertLess(actual_expect_diff, day_in_milliseconds)
            self.assertGreaterEqual(actual_expect_diff, 0)
            count += 1
        self.assertEqual(count, 150)
        it.close()


if __name__ == '__main__':
    add_runtime_params()
    unittest.main()
