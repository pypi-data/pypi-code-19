# -*- coding: utf-8 -*-

#    _                                 _
#   /_\    __ _   ___   _ __  __ _    (_)  ___
#  //_\\  / _` | / _ \ | '__|/ _` |   | | / _ \
# /  _  \| (_| || (_) || |  | (_| | _ | || (_) |
# \_/ \_/ \__, | \___/ |_|   \__,_|(_)|_| \___/
#        |___/


from agorasigsdk.server_address import ServerAddress

from random import randint

import logging
import requests
import time


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger('agorasigsdk')


CFG_LBS_N_RETRY = 5


def query_lbs(appid, url=''):
    """Query the location balance service for addresses of access points.
    Return None object if nothing fetched.

    Returns:
        servers (dict): Each key(str) has several addresses for value.(list).
    """
    is_ok = False
    if not url:
        url = 'http://lbs.sig.agora.io/getaddr?vid={0}'.format(appid)
    else:
        url = '{0}/getaddr?vid={1}'.format(url, appid)
    for i in range(CFG_LBS_N_RETRY):
        try:
            res = requests.get(url)
            if res:
                servers = res.json()
                is_ok = True
        except IOError as e:
            logger.exception('NET    {0}'.format(e))
            time.sleep(2)
            continue

        if is_ok:
            break
        else:
            time.sleep(1)

    return servers if is_ok else None


def format_websocket_url(ip, port):
    """Format and return a valid agora websocket url.

    Args:
        ip (str)
        port (int)
    """
    host = u'ws://{0}-sig-web.agora.io:{1}/'.format(
                    ip.replace('.', '-'), port)
    return host


def get_web2_addresses(lbs_access_points):
    """Get LBS server addresses and return web2 addresses.

    Args:
        lbs_access_points (list): The return of query_lbs().

    Returns:
        servers (list): A list of ServerAddress objects that represent web2
                        addresses.
    """
    logger.debug('NET    The lbs_access_points are {0}'.format(lbs_access_points))
    if lbs_access_points:
        servers = []
        web2s = lbs_access_points['web2']
        for web2 in web2s:
            address = ServerAddress(web2[0], web2[1])
            servers.append(address)
        return servers


def get_web2_url(servers):
    """Randomly pick a web2 server and translate it into a url.

    Return a tuple that includes the host url and a ServerAddress object.
    """
    if not servers:
        return (None, None)
    random_idx = randint(0, len(servers) - 1)
    server = servers[random_idx]
    host = format_websocket_url(server.ip, server.port)
    logger.info('NET    The web2 host url is {0}'.format(host))
    return (host, server)
