from foundrybot.resource import Resource
from pydash import pick


class DomainCrawlResource(Resource):
    def __init__(self, secret_key):
        super(secret_key)
        self.resource_name = 'DomainCrawl'

    def get(self, id):
        res = self.make_request({
            'method': 'GET',
            'params': {'id': id},
            'url': '/domain-crawls/{id}'
        })
        return res.doc

    def list(self, params):
        return self.make_request({
            'method': 'GET',
            'query': pick(params, 'limit', 'offset', 'url'),
            'url': '/domain-crawls'
        })

    def create(self, params):
        res = self.make_request({
            'method': 'POST',
            'data': pick(params, 'url', 'maxUrls', 'maxAge'),
            'url': '/domain-crawls'
        })
        return res.doc
