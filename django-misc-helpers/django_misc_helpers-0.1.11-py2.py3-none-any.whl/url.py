# -*- coding: utf-8 -*-
import sys

if sys.version_info[0] == 2:
    from urllib2 import Request, urlopen
    from urllib2 import URLError, HTTPError
else:
    from urllib.request import Request, urlopen
    from urllib.request import URLError, HTTPError


def load_url(url, post_data=None, headers={}):
    """Load url content"""
    req = Request(url, post_data, headers)  # POST data
    DEBUG = True
    try:
        urlh = urlopen(req)
    except HTTPError as e:
        if DEBUG:
            print(url, ' failed, code : ', e.code)
        return False
    except URLError as e:
        if DEBUG:
            print('We failed to reach a server - %s' % url)
            print('Reason: %s' % e.reason)
        return False

    not_readed = True
    i = 0
    real_url = url
    while not_readed:
        try:
            data = urlh.read()
        except:
            i = i + 1
            if i > 5:
                not_readed = False
        else:
            not_readed = False
            real_url = urlh.geturl()
            urlh.close()
    return data
