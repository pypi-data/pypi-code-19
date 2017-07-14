from foundrybot.resource import Resource
from pydash import pick


class UrlSnapshotLinkResource(Resource):
    def __init__(self, secret_key):
        super(secret_key)
        self.resource_name = 'UrlSnapshotLink'

    def list(self, params):
        return self.make_request({
            'method': 'GET',
            'query': pick(params, 'limit', 'offset', 'urlHref', 'urlSnapshotId', 'domainCrawlId'),
            'url': '/url-snapshot-links'
        })
