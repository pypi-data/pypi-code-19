import pprint
from json.decoder import JSONDecodeError

import requests as r

from .consensus import SiaConsensus
from .daemon import SiaDaemon
from .gateway import SiaGateway
from .host import SiaHost
from .hostdb import SiaHostDB
from .renter import SiaRenter
from .tpool import SiaTPool
from .wallet import SiaWallet


class Sia(object):
    def __init__(self, host="http://127.0.0.1", port=9980, unit='siacoin'):
        self.url = host + ":" + str(port)
        self.daemon = SiaDaemon(self)
        self.consensus = SiaConsensus(self)
        self.gateway = SiaGateway(self)
        self.host = SiaHost(self)
        self.hostdb = SiaHostDB(self)
        self.renter = SiaRenter(self)
        self.tpool = SiaTPool(self)
        self.wallet = SiaWallet(self)

    def get_api(self, endpoint, params=None):
        user_agent = {'User-agent': 'Sia-Agent'}
        resp = r.get(self.url + endpoint, headers=user_agent, params=params)
        try:
            resp.raise_for_status()
        except r.exceptions.HTTPError as e:
            raise SiaError(resp.json().get('message')) from e
        try:
            return resp.json()
        except JSONDecodeError:
            return resp.ok

    def post_api(self, endpoint, data=None):
        user_agent = {'User-agent': 'Sia-Agent'}
        resp = r.post(self.url + endpoint, headers=user_agent, data=data)
        try:
            resp.raise_for_status()
        except r.exceptions.HTTPError as e:
            raise SiaError(resp.json().get('message')) from e
        try:
            return resp.json()
        except JSONDecodeError:
            return resp.ok

    def hastings_to_siacoin(self, hastings):
        return hastings / 1000000000000000000000000


class SiaError(Exception):
    def __init__(self, message):
        self.message = message

if __name__ == '__main__':
    sc = Sia()
    pprint.pprint(sc.hostdb.host("ed25519:34db39ec43b507a415d3ca57348737bad6ee9725a00561a7f4ca1b25251dd7d3"))
