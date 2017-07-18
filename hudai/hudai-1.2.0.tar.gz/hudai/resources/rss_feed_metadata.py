from hudai.resource import Resource
from pydash import pick


class RssFeedMetadataResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client)
        self.resource_name = 'RssFeedMetadata'

    def get(self, uuid):
        return self.request({
            'method': 'GET',
            'params': {'uuid': uuid},
            'url': '/rss-feed-metadata/internal{uuid}'
        })

    def list(self, params):
        return self.request({
            'method': 'GET',
            'params': pick(params, 'feed_url', 'metadata', 'pulled_at'),
            'url': '/rss-feed-metadata/internal'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'data', 'feed_url', 'metadata', 'pulled_at'),
            'url': '/rss-feed-metadata/internal'
        })

    def update(self, params):
        return self.request({
            'method': 'PUT',
            'data': pick(params, 'data', 'feed_url', 'metadata', 'pulled_at'),
            'params': pick(params, 'uuid'),
            'url': '/rss-feed-metadata/internal{uuid}'
        })

    def delete(self, uuid):
        return self.request({
            'method': 'DELETE',
            'params': {'uuid': uuid},
            'url': '/rss-feed-metadata/internal{uuid}'
        })
