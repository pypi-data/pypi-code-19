from hudai.resource import Resource
from pydash import pick


class ArticleKeytermResource(Resource):
    def __init__(self, secret_key):
        Resource.__init__(self, secret_key)
        self.resource_name = 'ArticleKeyterm'

    def get(self, id):
        return self.make_request({
            'method': 'GET',
            'params': {'id': id},
            'url': '/article-keyterms/internal/{id}'
        })

    def search(self, params):
        return self.make_request({
            'method': 'GET',
            'params': pick(params, 'keyterm'),
            'url': '/article-keyterms/internal'
        })

    def create(self, params):
        return self.make_request({
            'method': 'POST',
            'data': pick(params, 'keyterm'),
            'url': '/article-keyterms/internal'
        })

    def update(self, params):
        return self.make_request({
            'method': 'PUT',
            'data': pick(params, 'keyterm'),
            'params'
            'url': '/article-keyterms/internal'
        })

    def delete(self, id):
        return self.make_request({
            'method': 'DELETE',
            'params': {'id': id},
            'url': '/article-keyterms/internal/{id}'
        })