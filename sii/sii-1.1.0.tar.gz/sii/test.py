# -*- coding: UTF-8 -*-
import logging

logging.basicConfig(level=logging.DEBUG)

from sii.server import *
from spec.testing_data import DataGenerator
from pprintpp import pprint
# Enviament de factures
data_gen = DataGenerator(contraparte_registered=True, invoice_registered=False)
in_invoice = data_gen.get_in_invoice()
out_invoice = data_gen.get_out_invoice()
in_refund = data_gen.get_in_refund_invoice()
out_refund = data_gen.get_out_refund_invoice()
s = SiiService('/home/gdalmau/Documents/SII/SSL/client.crt',
               '/home/gdalmau/Documents/SII/SSL/client.key',
               'https://sii-proxy.gisce.net:4443/test/', test_mode=True)
invoice = out_invoice
res = s.send(invoice)
pprint(res)

# # Consulta de factures
# s = SiiService('/home/gdalmau/Documents/SII/SSL/client.crt',
#                '/home/gdalmau/Documents/SII/SSL/client.key',
#                'https://sii-proxy.gisce.net:4443')
# res = s.query_invoice('out_invoice', '40351345F', 'Eduard Carreras Nadal',
#                       '2016', '12')
# from pprintpp import pprint
# pprint(res)

# Validació de NIF
# s = IDService('/home/miquel/Documents/SII/client_ssl/client.crt',
#               '/home/miquel/Documents/SII/client_ssl/client.key',
#               'https://sii-proxy.gisce.net:4443/nifs')
# d2 = [{'vat': '46724290C',
#        'name': 'Guillem Julia Blasi'},
#       {'vat': '40351345F',
#        'name': 'Eduard Carreras Nadal'},
#       {'vat': '82641631D',
#        'name': 'Dalmau Vila Dalmau'}
#       ]
# d1 = [{'vat': '46724290C',
#       'name': 'Guillem Julia Blasi'}]
# res = s.invalid_ids(d2, 1)
# print res
