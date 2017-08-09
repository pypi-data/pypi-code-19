# coding=utf8
from asyncio import futures

import functools
import geoip2.database
import concurrent.futures
from tornado import gen
import os


# This creates a Reader object. You should use the same object
# across multiple requests as creation of it is expensive.
reader = None

executor = concurrent.futures.ThreadPoolExecutor(2)

def load_reader(_dir):
    global reader
    reader = geoip2.database.Reader(
    os.path.abspath(
    os.path.join(
        _dir,
        './data/GeoIP2-Country-20170306.mmdb'
    ))
)
async def get_location(ip_address):
    '''
    Ip adresinin ülkesini getirmek için
    '''
    response = await futures.wrap_future(executor.submit(
        functools.partial(reader.city, ip_address)
    ))

    if not response:
        return None

    return {
        'country': response.country.name,
        'city': response.city.name,
        'latitude': response.location.latitude,
        'longitude': response.location.longitude
    }
