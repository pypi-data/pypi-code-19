from foundrybot.resource import Resource
from pydash import pick


class UrlSnapshotMediaResource(Resource):
    def __init__(self, secret_key):
        super(secret_key)
        self.resource_name = 'UrlSnapshotMedia'

    def list(self, params):
        return self.make_request({
            'method': 'GET',
            'query': pick(params, 'limit', 'offset', 'srcUrl', 'width', 'height', 'mimeType', 'urlSnapshotId', 'domainCrawlId'),
            'url': '/url-snapshot-media'
        })
