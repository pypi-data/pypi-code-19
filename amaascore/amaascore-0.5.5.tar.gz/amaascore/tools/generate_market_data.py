from __future__ import absolute_import, division, print_function, unicode_literals

from amaasutils.random_utils import random_string, random_decimal
from datetime import datetime, date
import pytz
import random

from amaascore.market_data.eod_price import EODPrice
from amaascore.market_data.fx_rate import FXRate
from amaascore.market_data.quote import Quote


def generate_eod_price(asset_manager_id=0, asset_id=None, business_date=date.today(), price=None):
    eod_price = EODPrice(asset_manager_id=asset_manager_id,
                         asset_id=asset_id or random_string(10),
                         business_date=business_date,
                         price=price or random_decimal())
    return eod_price


def generate_fx_rate(asset_manager_id=0, asset_id=None, rate_timestamp=None, rate=None, business_date=None,
                     rate_type='EOD'):
    now = datetime.utcnow().replace(tzinfo=pytz.utc, microsecond=0)
    rate_timestamp = rate_timestamp or now
    business_date = business_date or rate_timestamp.date() if type(rate_timestamp) == datetime else rate_timestamp
    fx_rate = FXRate(asset_manager_id=asset_manager_id,
                     asset_id=asset_id or random.choice(['USDJPY', 'USDSGD', 'EURUSD']),
                     business_date=business_date,
                     rate_timestamp=rate_timestamp,
                     rate=rate or random_decimal(),
                     rate_type=rate_type)
    return fx_rate


def generate_quote(asset_manager_id=0, asset_id=None, bid=None, ask=None):
    quote = Quote(asset_manager_id=asset_manager_id,
                  asset_id=asset_id or random_string(10),
                  bid=bid or random_decimal(),
                  ask=ask or random_decimal(),
                  quote_datetime=datetime.utcnow())
    return quote

