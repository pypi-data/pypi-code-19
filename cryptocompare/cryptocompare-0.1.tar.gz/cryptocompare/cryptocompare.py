import sys
import requests

# API
COIN_URL = 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms={}'

# FIELDS
PRICE = 'PRICE'
HIGH = 'HIGH24HOUR'
LOW = 'LOW24HOUR'
VOLUME = 'VOLUME24HOUR'
CHANGE = 'CHANGE24HOUR'
CHANGE_PERCENT = 'CHANGEPCT24HOUR'
MARKETCAP = 'MKTCAP'

# DEFAULTS
CURR = 'EUR'

def get_coin_info(coin, curr=CURR, fields=[PRICE, HIGH, LOW]):
    url = COIN_URL.format(coin, curr)
    try:
        coin_info = requests.get(url).json()['RAW'][coin][curr]
    except Exception as e:
        sys.exit('Error getting coin information. %s' % str(e))
    response = { 'COIN': coin }
    for field in fields:
        response[field] = coin_info[field]
    return response

def get_price(coin, curr=CURR):
    return get_coin_info(coin, curr, [PRICE])[PRICE]

def get_high(coin, curr=CURR):
    return get_coin_info(coin, curr, [HIGH])[HIGH]

def get_low(coin, curr=CURR):
    return get_coin_info(coin, curr, [LOW])[LOW]

def get_marketcap(coin, curr=CURR):
    return get_coin_info(coin, curr, [MARKETCAP])[MARKETCAP]
    
def get_change(coin, curr=None):
    if curr:
        return get_coin_info(coin, curr, [CHANGE])[CHANGE]
    else:
        return get_coin_info(coin, CURR, [CHANGE_PERCENT])[CHANGE_PERCENT]


