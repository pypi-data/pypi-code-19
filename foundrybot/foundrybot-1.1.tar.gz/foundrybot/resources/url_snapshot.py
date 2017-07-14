from foundrybot.resource import Resource
from pydash import pick


class UrlSnapshotResource(Resource):
    def __init__(self, secret_key):
        super(secret_key)
        self.resource_name = 'UrlSnapshot'

    def get(self, id):
        res = self.make_request({
            'method': 'GET',
            'params': {'id': id},
            'url': '/url-snapshots/{id}'
        })
        return res.doc

    def list(self, params):
        return self.make_request({
            'method': 'GET',
            'query': pick(params, 'limit', 'offset', 'urlHref', 'domainHostname'),
            'url': '/url-snapshots'
        })
