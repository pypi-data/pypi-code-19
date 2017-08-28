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
from time import time
import unittest

from nosqldb import COMMIT_NO_SYNC
from nosqldb import COMMIT_SYNC
from nosqldb import COMMIT_WRITE_NO_SYNC
from nosqldb import Durability
from nosqldb import IllegalArgumentException
from nosqldb import Row
from nosqldb import TimeToLive
from nosqldb import WriteOptions
from nosqldb import ONDB_DAYS
from nosqldb import ONDB_DURABILITY
from nosqldb import ONDB_HOURS
from nosqldb import ONDB_MASTER_SYNC
from nosqldb import ONDB_REPLICA_ACK
from nosqldb import ONDB_REPLICA_SYNC
from nosqldb import ONDB_RETURN_CHOICE
from nosqldb import ONDB_TIMEOUT
from nosqldb import ONDB_TIMEUNIT
from nosqldb import ONDB_TTL_DO_NOT_EXPIRE
from nosqldb import ONDB_TTL_TIMEUNIT
from nosqldb import ONDB_TTL_VALUE
from nosqldb import ONDB_UPDATE_TTL
from testSetup import add_runtime_params
from testSetup import get_store
from testSetup import table_name


class TestPutIfPresent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._store = get_store()
        cls._store.execute_sync("DROP TABLE IF EXISTS " + table_name)
        cls._store.refresh_tables()
        cls._store.execute_sync(
            "CREATE TABLE " + table_name + " (" +
            "id INTEGER, s STRING, l LONG, d DOUBLE, bool BOOLEAN, " +
            "bin BINARY, fbin BINARY(10), f FLOAT, arrStr ARRAY(STRING), " +
            "e ENUM(A, B, C, D), PRIMARY KEY (id) )")
        cls._store.refresh_tables()

    @classmethod
    def tearDownClass(cls):
        cls._store.execute_sync("DROP TABLE IF EXISTS " + table_name)
        cls._store.refresh_tables()
        cls._store.close()

    def setUp(self):
        self.store = get_store()
        self.table = table_name
        self.row = Row({'id': 100, 's': 'String value', 'l': 1234567890,
                    'd': 123.456, 'bool': True,
                    'bin': self.store.encode_base_64('binarydata'),
                    'fbin': self.store.encode_base_64('fixedfixed'),
                    'f': 1.2345, 'arrStr': ['X', 'Y', 'Z'],
                    'e': 'A'})
        self.version, row = self.store.put(self.table, self.row)

    def tearDown(self):
        self.store.delete(self.table, Row({'id': 100}))
        self.store.delete(self.table, Row({'id': 101}))
        self.store.close()

    def testPutIPNormal(self):
        # test with normal values and no special writeopts
        version, oldrow = self.store.put_if_present(
            self.table, self.row)
        primarykey = Row({'id': 100})
        newrow = self.store.get(self.table, primarykey)
        self.assertEqual(self.row, newrow)

    def testPutIPNsyNsyAll(self):
        # test with normal values and durabilityopts=NoSYNC, NoSYNC and All,
        # and returnValueVersion = NONE
        durability = Durability({
            ONDB_MASTER_SYNC: 'NO_SYNC',
            ONDB_REPLICA_SYNC: 'NO_SYNC',
            ONDB_REPLICA_ACK: 'ALL'})
        writeopts = WriteOptions({
            ONDB_DURABILITY: durability,
            ONDB_RETURN_CHOICE: 'NONE'})
        version, oldrow = self.store.put_if_present(
            self.table, self.row, writeopts)
        primarykey = Row({'id': 100})
        newrow = self.store.get(self.table, primarykey)
        self.assertEqual(self.row, newrow)

    def testPutIPNsyNsyNon(self):
        # test with normal values and durabilityopts=NoSYNC, NoSYNC and None,
        # and returnValueVersion = NONE
        durability = Durability({
            ONDB_MASTER_SYNC: 'NO_SYNC',
            ONDB_REPLICA_SYNC: 'NO_SYNC',
            ONDB_REPLICA_ACK: 'NONE'})
        writeopts = WriteOptions({
            ONDB_DURABILITY: durability,
            ONDB_RETURN_CHOICE: 'NONE'})
        version, oldrow = self.store.put_if_present(
            self.table, self.row, writeopts)
        primarykey = Row({'id': 100})
        newrow = self.store.get(self.table, primarykey)
        self.assertEqual(self.row, newrow)

    def testPutIPNsyNsySim(self):
        # test with normal values and durabilityopts=NoSYNC, NoSYNC
        # and SIMPLE_MAJORITY, and returnValueVersion = NONE
        durability = Durability({
            ONDB_MASTER_SYNC: 'NO_SYNC',
            ONDB_REPLICA_SYNC: 'NO_SYNC',
            ONDB_REPLICA_ACK: 'SIMPLE_MAJORITY'})
        writeopts = WriteOptions({
            ONDB_DURABILITY: durability,
            ONDB_RETURN_CHOICE: 'NONE'})
        version, oldrow = self.store.put_if_present(
            self.table, self.row, writeopts)
        primarykey = Row({'id': 100})
        newrow = self.store.get(self.table, primarykey)
        self.assertEqual(self.row, newrow)

    def testPutIPSynNsyAll(self):
        # test with normal values and durabilityopts=SYNC, NoSYNC and All,
        # and returnValueVersion = NONE
        durability = Durability({
            ONDB_MASTER_SYNC: 'SYNC',
            ONDB_REPLICA_SYNC: 'NO_SYNC',
            ONDB_REPLICA_ACK: 'ALL'})
        writeopts = WriteOptions({
            ONDB_DURABILITY: durability,
            ONDB_RETURN_CHOICE: 'NONE'})
        version, oldrow = self.store.put(self.table, self.row, writeopts)
        primarykey = Row({'id': 100})
        newrow = self.store.get(self.table, primarykey)
        self.assertEqual(self.row, newrow)

    def testPutIPSynNsyNon(self):
        # test with normal values and durabilityopts=SYNC, NoSYNC and None,
        # and returnValueVersion = NONE
        durability = Durability({
            ONDB_MASTER_SYNC: 'SYNC',
            ONDB_REPLICA_SYNC: 'NO_SYNC',
            ONDB_REPLICA_ACK: 'NONE'})
        writeopts = WriteOptions({
            ONDB_DURABILITY: durability,
            ONDB_RETURN_CHOICE: 'NONE'})
        version, oldrow = self.store.put_if_present(
            self.table, self.row, writeopts)
        primarykey = Row({'id': 100})
        newrow = self.store.get(self.table, primarykey)
        self.assertEqual(self.row, newrow)

    def testPutIPSynNsySim(self):
        # test with normal values and durabilityopts=SYNC, NoSYNC
        # and SIMPLE_MAJORITY and returnValueVersion = NONE
        durability = Durability({
            ONDB_MASTER_SYNC: 'SYNC',
            ONDB_REPLICA_SYNC: 'NO_SYNC',
            ONDB_REPLICA_ACK: 'SIMPLE_MAJORITY'})
        writeopts = WriteOptions({
            ONDB_DURABILITY: durability,
            ONDB_RETURN_CHOICE: 'NONE'})
        version, oldrow = self.store.put_if_present(
            self.table, self.row, writeopts)
        primarykey = Row({'id': 100})
        newrow = self.store.get(self.table, primarykey)
        self.assertEqual(self.row, newrow)

    def testPutIPNsySynAll(self):
        # test with normal values and durabilityopts=NoSYNC, SYNC and All,
        # and returnValueVersion = NONE
        durability = Durability({
            ONDB_MASTER_SYNC: 'NO_SYNC',
            ONDB_REPLICA_SYNC: 'SYNC',
            ONDB_REPLICA_ACK: 'ALL'})
        writeopts = WriteOptions({
            ONDB_DURABILITY: durability,
            ONDB_RETURN_CHOICE: 'NONE'})
        version, oldrow = self.store.put_if_present(
            self.table, self.row, writeopts)
        primarykey = Row({'id': 100})
        newrow = self.store.get(self.table, primarykey)
        self.assertEqual(self.row, newrow)

    def testPutIPNsySynNon(self):
        # test with normal values and durabilityopts=NoSYNC, SYNC and None,
        # and returnValueVersion = NONE
        durability = Durability({
            ONDB_MASTER_SYNC: 'NO_SYNC',
            ONDB_REPLICA_SYNC: 'SYNC',
            ONDB_REPLICA_ACK: 'NONE'})
        writeopts = WriteOptions({
            ONDB_DURABILITY: durability,
            ONDB_RETURN_CHOICE: 'NONE'})
        version, oldrow = self.store.put_if_present(
            self.table, self.row, writeopts)
        primarykey = Row({'id': 100})
        newrow = self.store.get(self.table, primarykey)
        self.assertEqual(self.row, newrow)

    def testPutIPNsySynSim(self):
        # test with normal values and durabilityopts=NoSYNC, SYNC
        # and SIMPLE_MAJORITY, and returnValueVersion = NONE
        durability = Durability({
            ONDB_MASTER_SYNC: 'NO_SYNC',
            ONDB_REPLICA_SYNC: 'SYNC',
            ONDB_REPLICA_ACK: 'SIMPLE_MAJORITY'})
        writeopts = WriteOptions({
            ONDB_DURABILITY: durability,
            ONDB_RETURN_CHOICE: 'NONE'})
        version, oldrow = self.store.put_if_present(
            self.table, self.row, writeopts)
        primarykey = Row({'id': 100})
        newrow = self.store.get(self.table, primarykey)
        self.assertEqual(self.row, newrow)

    def testPutIPSynSynAll(self):
        # test with normal values and durabilityopts=SYNC, SYNC and All,
        # and returnValueVersion = NONE
        durability = Durability({
            ONDB_MASTER_SYNC: 'SYNC',
            ONDB_REPLICA_SYNC: 'SYNC',
            ONDB_REPLICA_ACK: 'ALL'})
        writeopts = WriteOptions({
            ONDB_DURABILITY: durability,
            ONDB_RETURN_CHOICE: 'NONE'})
        version, oldrow = self.store.put_if_present(
            self.table, self.row, writeopts)
        primarykey = Row({'id': 100})
        newrow = self.store.get(self.table, primarykey)
        self.assertEqual(self.row, newrow)

    def testPutIPSynSynNon(self):
        # test with normal values and durabilityopts=SYNC, SYNC and None,
        # and returnValueVersion = NONE
        durability = Durability({
            ONDB_MASTER_SYNC: 'SYNC',
            ONDB_REPLICA_SYNC: 'SYNC',
            ONDB_REPLICA_ACK: 'NONE'})
        writeopts = WriteOptions({
            ONDB_DURABILITY: durability,
            ONDB_RETURN_CHOICE: 'NONE'})
        version, oldrow = self.store.put_if_present(
            self.table, self.row, writeopts)
        primarykey = Row({'id': 100})
        newrow = self.store.get(self.table, primarykey)
        self.assertEqual(self.row, newrow)

    def testPutIPSynSynSim(self):
        # test with normal values and durabilityopts=SYNC, SYNC
        # and SIMPLE_MAJORITY, and returnValueVersion = NONE
        durability = Durability({
            ONDB_MASTER_SYNC: 'SYNC',
            ONDB_REPLICA_SYNC: 'SYNC',
            ONDB_REPLICA_ACK: 'SIMPLE_MAJORITY'})
        writeopts = WriteOptions({
            ONDB_DURABILITY: durability,
            ONDB_RETURN_CHOICE: 'NONE'})
        version, oldrow = self.store.put_if_present(
            self.table, self.row, writeopts)
        primarykey = Row({'id': 100})
        newrow = self.store.get(self.table, primarykey)
        self.assertEqual(self.row, newrow)

    def testPutIPValue(self):
        # test with Durability.COMMIT_NO_SYNC and returnValueVersion = VALUE
        writeopts = WriteOptions({
            ONDB_DURABILITY: COMMIT_NO_SYNC,
            ONDB_RETURN_CHOICE: 'VALUE'})
        self.row['bool'] = False
        version2, oldrow = self.store.put_if_present(
            self.table, self.row, writeopts)
        self.row['bool'] = True
        self.assertEqual(self.row, oldrow)

    def testPutIPVersion(self):
        # test with Durability.COMMIT_SYNC and returnValueVersion = VERSION
        writeopts = WriteOptions({
            ONDB_DURABILITY: COMMIT_SYNC,
            ONDB_RETURN_CHOICE: 'VERSION'})
        self.row['bool'] = False
        version2, oldrow = self.store.put_if_present(
            self.table, self.row, writeopts)
        self.row['bool'] = True
        self.assertEqual(self.version, oldrow.get_version())

    def testPutIPValueVersion(self):
        # test with Durability.COMMIT_WRITE_NO_SYNC and returnValueVersion = ALL
        writeopts = WriteOptions({
            ONDB_DURABILITY: COMMIT_WRITE_NO_SYNC,
            ONDB_RETURN_CHOICE: 'ALL'})
        self.row['bool'] = False
        version2, oldrow = self.store.put_if_present(
            self.table, self.row, writeopts)
        self.row['bool'] = True
        self.assertEqual(self.row, oldrow)
        self.assertEqual(self.version, oldrow.get_version())

    def testPutIPSecondTimeout(self):
        # test with Durability.COMMIT_NO_SYNC, returnValueVersion = VALUE
        # and timeout = 1000 ms
        writeopts = WriteOptions({
            ONDB_DURABILITY: COMMIT_WRITE_NO_SYNC,
            ONDB_TIMEOUT: 1000,
            ONDB_RETURN_CHOICE: 'ALL'})
        version2, oldrow = self.store.put_if_present(
            self.table, self.row, writeopts)
        primarykey = Row({'id': 100})
        newrow = self.store.get(self.table, primarykey)
        self.assertEqual(self.row, newrow)

    def testPutIPNoTable(self):
        # test with an invalid table name
        self.assertRaises(IllegalArgumentException, self.store.put_if_present,
                          'NotValidTable', self.row)

    def testPutIPNegativeTimeout(self):
        # test with a negative timeout
        writeopts = WriteOptions({ONDB_TIMEOUT: -1})
        self.assertRaises(IllegalArgumentException, self.store.put_if_present,
                          self.table, self.row, writeopts)

    def testPutIPInvalidFields(self):
        # test with invalid fields in the row
        self.assertRaises(IllegalArgumentException, self.store.put_if_present,
                          self.table, {'invalidField': 'someValue'})

    def testPutIPAbsent(self):
        # test with a non-existing record, expect None as result
        self.row['id'] = 101
        version2, oldrow2 = self.store.put_if_present(self.table, self.row)
        primarykey = {'id': 101}
        crow = self.store.get(self.table, primarykey)
        self.assertEqual({}, oldrow2)
        self.assertEqual(None, crow)

    def testPutIPFalseUpdateRowWithoutTTL(self):
        ttl = TimeToLive({ONDB_TTL_VALUE: 5,
                          ONDB_TTL_TIMEUNIT: {ONDB_TIMEUNIT: ONDB_HOURS}})
        self.row.set_timetolive(ttl)
        # Try to update row without setting ONDB_UPDATE_TTL
        self.store.put_if_present(self.table, self.row)
        actual_expiration = self.row.get_expiration()
        self.assertEqual(actual_expiration, 0)
        # Try to update row setting {ONDB_UPDATE_TTL: False}
        write_op = WriteOptions({ONDB_UPDATE_TTL: False})
        self.store.put_if_present(self.table, self.row, write_op)
        actual_expiration = self.row.get_expiration()
        self.assertEqual(actual_expiration, 0)

    def testPutIPTrueUpdateRowWithoutTTL(self):
        day_in_milliseconds = 24 * 60 * 60 * 1000
        ttl = TimeToLive({ONDB_TTL_VALUE: 3,
                          ONDB_TTL_TIMEUNIT: {ONDB_TIMEUNIT: ONDB_DAYS}})
        expect_expiration = ttl.calculate_expiration(time() * 1000)
        self.row.set_timetolive(ttl)
        write_op = WriteOptions({ONDB_UPDATE_TTL: True})
        self.store.put_if_present(self.table, self.row, write_op)
        actual_expiration = self.row.get_expiration()
        actual_expect_diff = actual_expiration - expect_expiration
        self.assertGreater(actual_expiration, 0)
        self.assertLess(actual_expect_diff, day_in_milliseconds)
        self.assertGreaterEqual(actual_expect_diff, 0)

    def testPutIPFalseUpdateRowWithTTL(self):
        # Prepare a row with TTL information
        ttl = TimeToLive({ONDB_TTL_VALUE: 5,
                          ONDB_TTL_TIMEUNIT: {ONDB_TIMEUNIT: ONDB_HOURS}})
        self.row.set_timetolive(ttl)
        write_op = WriteOptions({ONDB_UPDATE_TTL: True})
        self.store.put_if_present(self.table, self.row, write_op)
        old_expiration = self.row.get_expiration()
        self.assertGreater(old_expiration, 0)
        # Try to update the row above without setting ONDB_UPDATE_TTL
        ttl = TimeToLive({ONDB_TTL_VALUE: 3,
                          ONDB_TTL_TIMEUNIT: {ONDB_TIMEUNIT: ONDB_DAYS}})
        self.row.set_timetolive(ttl)
        self.store.put_if_present(self.table, self.row)
        new_expiration = self.row.get_expiration() 
        self.assertEqual(old_expiration, new_expiration)
        # Try to update the row above setting {ONDB_UPDATE_TTL: False}
        write_op = WriteOptions({ONDB_UPDATE_TTL: False})
        self.store.put_if_present(self.table, self.row, write_op)
        new_expiration = self.row.get_expiration() 
        self.assertEqual(old_expiration, new_expiration)

    def testPutIPTrueUpdateRowWithTTL(self):
        hour_in_milliseconds = 60 * 60 * 1000
        # Prepare a row with TTL information
        ttl = TimeToLive({ONDB_TTL_VALUE: 3,
                          ONDB_TTL_TIMEUNIT: {ONDB_TIMEUNIT: ONDB_DAYS}})
        self.row.set_timetolive(ttl)
        write_op = WriteOptions({ONDB_UPDATE_TTL: True})
        self.store.put_if_present(self.table, self.row, write_op)
        old_expiration = self.row.get_expiration()
        self.assertGreater(old_expiration, 0)
        # Try to update the TTL of the above row from 3 days to 5 hours
        ttl = TimeToLive({ONDB_TTL_VALUE: 5,
                          ONDB_TTL_TIMEUNIT: {ONDB_TIMEUNIT: ONDB_HOURS}})
        expect_expiration = ttl.calculate_expiration(time() * 1000)
        self.row.set_timetolive(ttl)
        write_op = WriteOptions({ONDB_UPDATE_TTL: True})
        self.store.put_if_present(self.table, self.row, write_op)
        new_expiration = self.row.get_expiration()
        new_expect_diff = new_expiration - expect_expiration
        self.assertGreater(new_expiration, 0)
        self.assertNotEqual(old_expiration, new_expiration)
        self.assertLess(new_expect_diff, hour_in_milliseconds)
        self.assertGreaterEqual(new_expect_diff, 0)
        # Try to update the TTL of the above row from 5 hours to never expires
        ttl = ONDB_TTL_DO_NOT_EXPIRE
        self.row.set_timetolive(ttl)
        write_op = WriteOptions({ONDB_UPDATE_TTL: True})
        self.store.put_if_present(self.table, self.row, write_op)
        new_expiration = self.row.get_expiration()
        self.assertEqual(new_expiration, 0)

    def testPutIPUpdateRowWithTTLToWithoutTTL(self):
        row_with_ttl = Row(self.row)
        # Prepare a row with TTL information
        ttl = TimeToLive({ONDB_TTL_VALUE: 5,
                          ONDB_TTL_TIMEUNIT: {ONDB_TIMEUNIT: ONDB_HOURS}})
        row_with_ttl.set_timetolive(ttl)
        write_op = WriteOptions({ONDB_UPDATE_TTL: True})
        self.store.put_if_present(self.table, row_with_ttl, write_op)
        old_expiration = row_with_ttl.get_expiration()
        self.assertGreater(old_expiration, 0)
        # Try to update the row with TTL to a row without TTL, leaving
        # ONDB_UPDATE_TTL not set.
        self.store.put_if_present(self.table, self.row)
        new_expiration = self.row.get_expiration()
        self.assertEqual(old_expiration, new_expiration)
        # Try to update the row with TTL to a row without TTL, setting
        # {ONDB_UPDATE_TTL: False}
        write_op = WriteOptions({ONDB_UPDATE_TTL: False})
        self.store.put_if_present(self.table, self.row, write_op)
        new_expiration = self.row.get_expiration() 
        self.assertEqual(old_expiration, new_expiration)
        # Try to update the row with TTL to a row without TTL, setting
        # {ONDB_UPDATE_TTL: True}
        write_op = WriteOptions({ONDB_UPDATE_TTL: True})
        self.store.put_if_present(self.table, self.row, write_op)
        new_expiration = self.row.get_expiration() 
        self.assertEqual(new_expiration, 0)
        self.assertNotEqual(old_expiration, new_expiration)


if __name__ == '__main__':
    add_runtime_params()
    unittest.main()
