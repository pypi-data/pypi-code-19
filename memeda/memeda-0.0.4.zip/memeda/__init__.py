#!/usr/bin/env python
# encoding:utf-8
from urllib.request import urlretrieve

def memeda():
    print('么么哒！(づ￣ 3￣)づ')


def dl(url):
    try:
        urlretrieve(url,url.split('/')[-1])
        print('{}下载完成！'.format(url))
    except:
        print('地址错误')
