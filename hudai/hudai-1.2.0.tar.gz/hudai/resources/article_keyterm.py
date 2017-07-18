from hudai.resource import Resource
from pydash import pick


class ArticleKeytermResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client)
        self.resource_name = 'ArticleKeyterm'

    def get(self, id):
        return self.request({
            'method': 'GET',
            'params': {'id': id},
            'url': '/article-keyterms/internal/{id}'
        })

    def list(self, params):
        return self.request({
            'method': 'GET',
            'params': pick(params, 'keyterm'),
            'url': '/article-keyterms/internal'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'keyterm'),
            'url': '/article-keyterms/internal'
        })

    def update(self, params):
        return self.request({
            'method': 'PUT',
            'data': pick(params, 'keyterm'),
            'url': '/article-keyterms/internal'
        })

    def delete(self, id):
        return self.request({
            'method': 'DELETE',
            'params': {'id': id},
            'url': '/article-keyterms/internal/{id}'
        })
