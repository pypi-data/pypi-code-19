"""
Constants used through the program

DO NOT MODIFY THESE VALUES
"""
from __future__ import unicode_literals


TIME_OUT = 10

DEFAULT_AUTO_SOURCE_IGNORES = ['Vehicle', 'CI MISSING ZONE', 'DECON',
                               'INVALID KITS', 'DOWN TRAY', 'LOOSE', 'INST',
                               'Location Bin', 'Temp']

STOCK_TABLE_HEADERS = ['product_number', 'description', 'lot_serial',
                       'container_type', 'container', 'location_type',
                       'location', 'qoh', 'qav', 'qr', 'zsms_hold']

TRANSFER_TABLE_HEADERS = ['transfer_number', 'status', 'location_type',
                          'location', 'assigned_to', 'from_container_type',
                          'from_container', 'to_container_type', 'to_container',
                          'product_number', 'description', 'qty']

STOCK_TABLE_CLASS_ID = 'GKCQ-U1BKM'
TRANSFER_TABLE_CLASS_ID = 'GKCQ-U1BKM'

STOCK_TABLE_CLASS_INDEX = 2
TRANSFER_TABLE_CLASS_INDEX = 7

ENTER_KEY = '\ue007'