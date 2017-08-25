import json
import re

import pycurl
from bs4 import UnicodeDammit

from netboy.util.soup import Soup


class Result:
    def __init__(self, setup=None):
        self.setup = setup

    def response(self, payload, response, json_data=False):
        if not self.setup:
            return None
        charset = None
        if 'content-type' in self.setup.headers:
            content_type = self.setup.headers['content-type'].lower()
            match = re.search('charset=(\S+)', content_type)
            if match:
                charset = match.group(1)
                print('Decoding using %s' % charset)
        body = self.setup.databuf.getvalue()
        if len(body) == 0:
            data = ''
            charset = 'utf-8'
        else:
            if charset is None:
                dammit = UnicodeDammit(body, ["utf-8", "gb2312", "gbk", "big5", "gb18030"], smart_quotes_to="html")
                data = dammit.unicode_markup
                charset = dammit.original_encoding
            else:
                data = body.decode(charset, 'ignore')
        # headers.remove({})
        self.setup.headers['content'] = [h for h in self.setup.headers['content'] if len(h) > 0]
        sp_lxml = Soup(data, 'lxml')
        sp_html = Soup(data, 'html.parser')
        response.update({
            'url': payload.get('url'),
            'title': sp_lxml.get_title(),
            'links': sp_lxml.get_links(),
            'links2': sp_lxml.get_links2(),
            'metas': sp_lxml.get_metas(),
            'images': sp_lxml.get_images(),
            'scripts': sp_lxml.get_scripts(),
            'text': sp_html.get_text(),
            'data': json.loads(data) if json_data else data,
            'headers': self.setup.headers,
            'charset': charset,
            'spider': 'pycurl',
            'payload': payload,
        })
        return response

    def result(self, curl, state='normal', resp=None):
        effective_url = curl.getinfo(pycurl.EFFECTIVE_URL)
        primary_ip = curl.getinfo(pycurl.PRIMARY_IP)
        primary_port = curl.getinfo(pycurl.PRIMARY_PORT)
        local_ip = curl.getinfo(pycurl.LOCAL_IP)
        local_port = curl.getinfo(pycurl.LOCAL_PORT)
        speed_download = curl.getinfo(pycurl.SPEED_DOWNLOAD)
        size_download = curl.getinfo(pycurl.SIZE_DOWNLOAD)
        redirect_time = curl.getinfo(pycurl.REDIRECT_TIME)
        redirect_count = curl.getinfo(pycurl.REDIRECT_COUNT)
        redirect_url = curl.getinfo(pycurl.REDIRECT_URL)
        http_code = curl.getinfo(pycurl.HTTP_CODE)
        response_code = curl.getinfo(pycurl.RESPONSE_CODE)
        total_time = curl.getinfo(pycurl.TOTAL_TIME)
        content_type = curl.getinfo(pycurl.CONTENT_TYPE)
        namelookup_time = curl.getinfo(pycurl.NAMELOOKUP_TIME)
        info_filetime = curl.getinfo(pycurl.INFO_FILETIME)
        http_connectcode = curl.getinfo(pycurl.HTTP_CONNECTCODE)
        starttransfer_time = curl.getinfo(pycurl.STARTTRANSFER_TIME)
        pretransfer_time = curl.getinfo(pycurl.PRETRANSFER_TIME)
        header_size = curl.getinfo(pycurl.HEADER_SIZE)
        request_size = curl.getinfo(pycurl.REQUEST_SIZE)
        ssl_verifyresult = curl.getinfo(pycurl.SSL_VERIFYRESULT)
        num_connects = curl.getinfo(pycurl.NUM_CONNECTS)
        content_length_download = curl.getinfo(pycurl.CONTENT_LENGTH_DOWNLOAD)

        ret = {
            'effective_url': effective_url,
            'primary_ip': primary_ip,
            'primary_port': primary_port,
            'local_ip': local_ip,
            'local_port': local_port,
            'speed_download': speed_download,
            'size_download': size_download,
            'redirect_time': redirect_time,
            'redirect_count': redirect_count,
            'redirect_url': redirect_url,
            'http_code': http_code,
            'response_code': response_code,
            'total_time': total_time,
            'content_type': content_type,
            'namelookup_time': namelookup_time,
            'info_filetime': info_filetime,
            'http_connectcode': http_connectcode,
            'starttransfer_time': starttransfer_time,
            'pretransfer_time': pretransfer_time,
            'header_size': header_size,
            'request_size': request_size,
            'ssl_verifyresult': ssl_verifyresult,
            'num_connects': num_connects,
            'content_length_download': content_length_download,
            'spider': 'pycurl',
            'state': state,
        }
        if resp:
            ret.update(resp)
        return ret
