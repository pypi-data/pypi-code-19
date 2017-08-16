#!/usr/bin/env python
# -*- coding:utf-8 -*- 
"""
INDEX DATA
Created on 2017年8月13日
@author: Jimmy Liu
@group : waditu
@contact: jimmysoa@sina.cn
"""

import pandas as pd
from pandas.compat import StringIO
from tushare.stock import cons as ct
import numpy as np
import time
import json
import re
import lxml.html
from lxml import etree
from tushare.util import dateu as du
from tushare.stock import ref_vars as rv
try:
    from urllib.request import urlopen, Request
except ImportError:
    from urllib2 import urlopen, Request


def bdi(btype='D', retry_count=3,
                pause=0.001):
    for _ in range(retry_count):
        time.sleep(pause)
        try:
            request = Request(ct.BDI_URL%(ct.P_TYPE['http'], ct.DOMAINS['v500']))
            lines = urlopen(request, timeout = 10).read()
            if len(lines) < 100: #no data
                return None
        except Exception as e:
                print(e)
        else:
            strlines = lines.decode('utf-8') if ct.PY3 else lines
            if btype == 'D':
                reg = re.compile(r'\"chart_data\",\"(.*?)\"\);') 
                lines = reg.findall(strlines)
                lines = lines[0]
                lines = lines.replace('chart', 'table').\
                        replace('</series><graphs>', '').\
                        replace('</graphs>', '').\
                        replace('series', 'tr').\
                        replace('value', 'td').\
                        replace('graph', 'tr').\
                        replace('graphs', 'td')
                df = pd.read_html(lines, encoding='utf8')[0]
                df = df.T
                df.columns = ['date', 'index']
                df['date'] = df['date'].map(lambda x: x.replace(u'年', '-')).map(lambda x: x.replace(u'月', '-')).map(lambda x: x.replace(u'日', ''))
                df['date'] = pd.to_datetime(df['date'])
                df['index'] = df['index'].astype(float)
                df = df.sort('date', ascending=False).reset_index(drop = True)
                df['change'] = df['index'].pct_change(-1)
                df['change'] = df['change'] * 100
                df['change'] = df['change'].map(lambda x: '%.2f' % x)
                return df
            else:
                html = lxml.html.parse(StringIO(strlines))
                res = html.xpath("//table[@class=\"style33\"]/tr/td/table[last()]/tr")
                if ct.PY3:
                    sarr = [etree.tostring(node).decode('utf-8') for node in res]
                else:
                    sarr = [etree.tostring(node) for node in res]
                sarr = ''.join(sarr)
                sarr = '<table>%s</table>'%sarr
                print(sarr)
                df = pd.read_html(sarr)[0]
                df.columns = ['month', 'index']
                df = df[1:]
                return df

