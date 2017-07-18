from hudai.resource import Resource
from pydash import pick


class ArticleHighlightResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client)
        self.resource_name = 'ArticleHighlight'

    def get(self, params):
        return self.request({
            'method': 'GET',
            'params': pick(params, 'url', 'user_id'),
            'url': '/article-highlights/internal/{url}/{user_id}'
        })

    def list(self, params):
        return self.request({
            'method': 'GET',
            'params': pick(params, 'user_id'),
            'url': '/article-highlights/internal'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'url', 'user_id', 'body'),
            'url': '/article-highlights/internal'
        })

    def update(self, params):
        return self.request({
            'method': 'PUT',
            'data': pick(params, 'body'),
            'params': pick(params, 'url', 'user_id'),
            'url': '/article-highlights/internal/{url}/{user_id}'
        })

    def delete(self, params):
        return self.request({
            'method': 'DELETE',
            'params': pick(params, 'url', 'user_id'),
            'url': '/article-highlights/internal/{url}/{user_id}'
        })
