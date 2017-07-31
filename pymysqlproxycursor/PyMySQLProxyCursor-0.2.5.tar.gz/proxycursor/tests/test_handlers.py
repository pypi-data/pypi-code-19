# -*- coding: utf-8 -*-

from __future__ import print_function

import pymysql
import proxycursor

from proxycursor.tests import base


__all__ = ['TestHandlers']


def sale_reco_idx_on_insert(cursor, tblname):
    cursor.execute('SELECT idx FROM {0} WHERE idx = (SELECT LAST_INSERT_ID())'.format(tblname))
    result = cursor.fetchone()
    return result['idx']


def sale_reco_idx_on_update(cursor, tblname):
    cursor.execute('SELECT idx FROM {0} ORDER BY updated_at DESC LIMIT 1'.format(tblname))
    result = cursor.fetchone()
    return result['idx']


def saleidx_on_insert(cursor, tblname):
    cursor.execute('SELECT idx, saleidx FROM {0} WHERE idx = (SELECT LAST_INSERT_ID())'.format(tblname))
    result = cursor.fetchone()
    return result['saleidx']


def saleidx_on_update(cursor, tblname):
    cursor.execute('SELECT idx, saleidx FROM {0} ORDER BY last_update DESC LIMIT 1'.format(tblname))
    result = cursor.fetchone()
    return result['saleidx']


def sync_available_room(cursor, sale_reco_idx):
    query = """
      UPDATE
        sale_reco AS SR
      SET
        SR.available_rooms = SR.cap - (
          SELECT
            COUNT(*)
          FROM
            reservation_rec AS RR
          WHERE 1=1
            AND RR.saleidx = SR.idx
            AND RR.is_cancel = FALSE
        )
      WHERE SR.idx = %s
    """
    cursor.execute(query, (sale_reco_idx,))


class SaleRecoSync(object):
    def __init__(self):
        self.tblname = 'sale_reco'

    def after_insert(self, **kwargs):
        cursor = kwargs['cursor']
        idx = sale_reco_idx_on_insert(cursor, self.tblname)
        sync_available_room(cursor, idx)

    def after_update(self, **kwargs):
        cursor = kwargs['cursor']
        idx = sale_reco_idx_on_update(cursor, self.tblname)
        sync_available_room(cursor, idx)


class ReservationRecSync(object):
    def __init__(self):
        self.tblname = 'reservation_rec_single'

    def after_insert(self, **kwargs):
        cursor = kwargs['cursor']
        idx = saleidx_on_insert(cursor, self.tblname)
        sync_available_room(cursor, idx)

    def after_update(self, **kwargs):
        cursor = kwargs['cursor']
        idx = saleidx_on_update(cursor, self.tblname)
        sync_available_room(cursor, idx)


class TestHandlers(base.PyMySQLProxyCursorTestCase):

    def setUp(self):
        super(TestHandlers, self).setUp()
        conn = self.connections[0]
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        self.cursor = proxycursor.wrap(cursor, handlers=[SaleRecoSync(), ReservationRecSync()])

    def test_hook_after_insert_sale_reco(self):
        pass

    def test_hook_after_cancel_reservation(self):
        row = self._get_random_reservation()
        reservation_rec_idx = row['idx']
        sale_reco_idx = row['saleidx']

        expect_available_rooms = self._compute_available_rooms(sale_reco_idx)
        print ('Before Rooms:', expect_available_rooms)

        self._cancel_reservation(reservation_rec_idx)
        print ('Canceled..', reservation_rec_idx)

        actual_available_rooms = self._get_actual_available_rooms(sale_reco_idx)
        print ('After Rooms:', actual_available_rooms)

        self.assertEqual(expect_available_rooms + 1, actual_available_rooms)

    def test_lastrowid_for_non_hooking_table(self):
        query = """
          INSERT INTO 
            reservation_rec_single (
              user_idx, 
              hotel_idx, 
              room_idx, 
              payment_type, 
              checkin_date, 
              checkout_date, 
              kcpno, tid,
              bonus, 
              room_name, 
              discount_total, 
              deposit_total, 
              selling_price_total, 
              delta_price_total,
              guest_name, 
              guest_phone, 
              guest_email, 
              guest_transportation, 
              reg_date, refund_type, 
              hotel_refund_idx, 
              rating)
          VALUES
            ( '9797', '368', '177318', 0, '2017-07-05 15:30:00', '2017-07-06 19:00:00',
            'INI0Dwp', 'Dwp20170705153256681424', '0', '테스트 더블', 63150, '60000',
            '66660', -3510, 'dh00', '+82 (0)1033435072', 'dh00@dh.com',
            'UNKNOWN', '2017-07-05 15:32:56.681398', '', NULL, -1)
        """
        self.cursor.execute(query)
        self.assertNotEqual(self.cursor.lastrowid, 0)

    def _get_random_reservation(self):
        query = """
          SELECT
            RS.idx, RR.saleidx
          FROM
            reservation_rec RR
          LEFT JOIN reservation_rec_single RS
            ON RS.idx = RR.reservation_rec_single_idx
          WHERE 1=1
            AND RS.checkin_date > CURDATE()
            AND RR.is_cancel = FALSE    
          ORDER BY
            RAND()
          LIMIT 1
        """
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result

    def _cancel_reservation(self, reservation_rec_idx):
        query = """
          UPDATE
            reservation_rec
          SET
            is_cancel = 1,
            cancel_date = NOW()
          WHERE
            idx = %s
        """
        self.cursor.execute(query, (reservation_rec_idx,))

    def _compute_available_rooms(self, sale_reco_idx):
        query = """
          SELECT
            S.cap - (
              SELECT
                count(*)
              FROM 
                reservation_rec_single RS
              LEFT JOIN reservation_rec RR
                ON RS.idx = RR.reservation_rec_single_idx
              WHERE 1=1
                AND RR.saleidx = %s
                AND RR.is_cancel = 0
              ) as expect_available_rooms
          FROM
            sale_reco S
          WHERE
            S.idx = %s
        """
        self.cursor.execute(query, (sale_reco_idx,sale_reco_idx))
        result = self.cursor.fetchone()
        return result['expect_available_rooms']

    def _get_actual_available_rooms(self, sale_reco_idx):
        query = """
          SELECT
            available_rooms
          FROM 
            sale_reco
          WHERE
            idx = %s
        """
        self.cursor.execute(query, (sale_reco_idx,))
        result = self.cursor.fetchone()
        return result['available_rooms']
