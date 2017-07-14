import requests


def json(f):
    def wrapper(*args):
        ret = f(*args)
        ret.raise_for_status
        return ret.json()
    return wrapper


class Srv(object):
    def __init__(self, host):
        self.host = host

    def Url(self, url):
        return self.host + url

    @json
    def C(self, url, doc):
        return requests.post(self.Url(url), json=doc)

    @json
    def Q(self, url, qry):
        return requests.get(self.host+url, params=qry, json=[])

    @json
    def R(self, url):
        return requests.get(self.Url(url), json=[])

    @json
    def U(self, url, doc):
        return requests.put(self.Url(url), json=doc)

    @json
    def D(self, url):
        return requests.delete(self.Url(url))

