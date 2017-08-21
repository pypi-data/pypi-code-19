"""
To play with nao functionality in a finance style
interactive console

Run as ``python -m nao`` or ``pym nao`` or ``nao``
using the nao extensions for python

"""

from future.utils import python_2_unicode_compatible

from babel.numbers import format_currency

@python_2_unicode_compatible
class Currency(object):

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

M = Mil = 10**6
B = Mrd = 10**9
T = Bil = 10**12

RMB = Currency('RMB')
HUF = Currency('HUF')

def add_currencies():
    """use datebase or list or something"""

add_currencies()

base_currency = HUF

@python_2_unicode_compatible
class Amount(object):

    def __init__(self, amount, currency=base_currency):
        self.amount = amount
        self.currency = currency

    def __str__(self):
        return format_currency(self.amount, self.currency)




