from hudai.resource import Resource
from pydash import pick


class NewsApiArticleResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/news-api-articles')
        self.resource_name = 'NewsApiArticle'

    def get(self, uuid):
        return self.request({
            'method': 'GET',
            'params': {'uuid': uuid},
            'url': '/internal/{uuid}'
        })

    def list(self, params):
        return self.request({
            'method': 'GET',
            'params': pick(params, 'published_at', 'source'),
            'url': '/internal'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'data', 'published_at', 'source'),
            'url': '/internal'
        })

    def update(self, params):
        return self.request({
            'method': 'PUT',
            'data': pick(params, 'data', 'published_at', 'source'),
            'params': pick(params, 'uuid'),
            'url': '/internal/{uuid}'
        })

    def delete(self, uuid):
        return self.request({
            'method': 'DELETE',
            'params': {'uuid': uuid},
            'url': '/internal/{uuid}'
        })
