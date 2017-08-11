from __future__ import absolute_import, division, print_function, unicode_literals

from amaascore.market_data.eod_price import EODPrice
from amaascore.market_data.fx_rate import FXRate


def json_to_eod_price(json_eod_price):
    eod_price = EODPrice(**json_eod_price)
    return eod_price


def json_to_fx_rate(json_fx_rate):
    fx_rate = FXRate(**json_fx_rate)
    return fx_rate

