import tornado
from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado import gen
from urllib.parse import urljoin
import concurrent.futures
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import logging
import asyncio

executor = concurrent.futures.ThreadPoolExecutor(4)


def __get_rate_from_xml(xml, currency_code):
    xml = ET.fromstring(xml)

    currencies = xml.findall('Currency')

    f = filter(lambda x: x.attrib['CurrencyCode'] == currency_code, currencies)
    if f:
        f = f[0]
        return float(f.find('BanknoteSelling').text)



async def get_rate(currency_code, date=None):
    """
    yield currency_helper.get_rate('USD', datetime(2016,05,30))
    """

    base_url = 'http://www.tcmb.gov.tr/kurlar/'
    if not date:
        url = 'today.xml'
    else:
        url = '%s/%s.xml' % (date.strftime('%Y%m'), date.strftime('%d%m%Y'))

    request = tornado.httpclient.HTTPRequest(
        method='GET',
        url=urljoin(
            base_url,
            url
        )
    )

    logging.info(request.url)

    http_client = AsyncHTTPClient()
    try:
        response = await http_client.fetch(request)
        rate = await asyncio.futures.wrap_future(
            executor.submit(__get_rate_from_xml, response.body, currency_code))
        return rate
    except HTTPError as e:
        if e.response.code == 404:
            date = date + timedelta(days=-1)
            new_rate = await get_rate(currency_code, date)
            raise gen.Return(new_rate)

        raise e
