# -*- coding: utf-8 -*-

import unittest2

from proxycursor import utils


__all__ = ['TestSQLParser']


class TestSQLParser(unittest2.TestCase):

    def test_insert(self):
        sql = """
          INSERT INTO `user` (id, name, email)
          VALUES ('1', 'test', 'test@gmail.com')
        """
        dml_type, tables = utils.parser.extract_tables(sql)
        self.assertEqual(dml_type, 'INSERT')
        self.assertListEqual(tables, ['user'])

    def test_insert_select(self):
        sql = """
          INSERT INTO
            Customer (FirstName, LastName, City, Country, Phone)
          SELECT
            LEFT(ContactName, CHARINDEX(' ',ContactName) - 1) AS FirstName,
            SUBSTRING(ContactName, CHARINDEX(' ',ContactName) + 1, 100) AS LastName,
            City,
            Country,
            Phone
          FROM Supplier
          WHERE Country = 'Canada'
        """
        dml_type, tables = utils.parser.extract_tables(sql)
        self.assertEqual(dml_type, 'INSERT')
        self.assertListEqual(tables, ['customer'])

    def test_insert_select_complex(self):
        sql = """
          INSERT INTO `sale_reco` (
            `hotelidx`,
            `roomidx`,
            `price`,
            `discount`,
            `sday`,
            `cap`,
            `checkin`,
            `checkout`,
            `deposit`,
            `bed_type`,
            `selling_price`,
            `delta_price`,
            `site_special_code`,
            `is_dailychoice`,
            `is_block`,
            `hide`
          ) SELECT
            hotel.idx AS `hotelidx`,
            193728 AS `roomidx`,
            IF(IFNULL(CASE DAYOFWEEK('2017-07-09')
              WHEN 1 THEN room_info_extra.sunday_price
              WHEN 2 THEN room_info_extra.tuesday_price
              WHEN 3 THEN room_info_extra.wednesday_price
              WHEN 4 THEN room_info_extra.wednesday_price
              WHEN 5 THEN room_info_extra.thursday_price
              WHEN 6 THEN room_info_extra.friday_price
              WHEN 7 THEN room_info_extra.saturday_price
            END, room_info.price) >= 63150,
            IFNULL(CASE DAYOFWEEK('2017-07-09')
              when 1 then room_info_extra.sunday_price
              when 2 then room_info_extra.tuesday_price
              when 3 then room_info_extra.wednesday_price
              when 4 then room_info_extra.wednesday_price
              when 5 then room_info_extra.thursday_price
              when 6 then room_info_extra.friday_price
              when 7 then room_info_extra.saturday_price
            END, room_info.price), 0) AS price,
            63150 AS `discount`,
            '2017-07-09' AS `sday`,
            5 AS `cap`,
            CONCAT('2017-07-09 ', IFNULL(CASE DAYOFWEEK('2017-07-09')
              WHEN 1 THEN room_info_extra.sunday_checkin
              WHEN 2 THEN room_info_extra.tuesday_checkin
              WHEN 3 THEN room_info_extra.wednesday_checkin
              WHEN 4 THEN room_info_extra.wednesday_checkin
              WHEN 5 THEN room_info_extra.thursday_checkin
              WHEN 6 THEN room_info_extra.friday_checkin
              WHEN 7 THEN room_info_extra.saturday_checkin
            END, CONCAT(hotel.checkin, ":00:00"))) AS checkin,
            CONCAT(ADDDATE(DATE('2017-07-09'), interval 1 day), ' ', IFNULL(CASE DAYOFWEEK('2017-07-09')
              WHEN 1 THEN room_info_extra.sunday_checkout
              WHEN 2 THEN room_info_extra.tuesday_checkout
              WHEN 3 THEN room_info_extra.wednesday_checkout
              WHEN 4 THEN room_info_extra.wednesday_checkout
              WHEN 5 THEN room_info_extra.thursday_checkout
              WHEN 6 THEN room_info_extra.friday_checkout
              WHEN 7 THEN room_info_extra.saturday_checkout
            END, CONCAT(hotel.checkout, ":00:00"))) AS checkout,
              60000 AS `deposit`,
              room_info_extra.bed_type AS `bed_type`,
              63150 AS `selling_price`,
              0 AS `delta_price`,
              null AS `site_special_code`,
              0 AS `is_dailychoice`,
              0 AS `is_block`,
              0 AS `hide`
            FROM
              hotel, room_info, dh_extra.room_info_extra
            WHERE
              hotel.idx = 368 AND
              room_info_extra.room_info_idx = room_info.idx AND
              room_info.idx = 193728
            """
        dml_type, tables = utils.parser.extract_tables(sql)
        self.assertEqual(dml_type, 'INSERT')
        self.assertListEqual(tables, ['sale_reco'])

    def test_update(self):
        sql = """
          UPDATE
            reservation_rec
          SET
            is_cancel = 1
          WHERE
            reservation_rec_single_idx = 78234259
        """
        dml_type, tables = utils.parser.extract_tables(sql)
        self.assertEqual(dml_type, 'UPDATE')
        self.assertListEqual(tables, ['reservation_rec'])

