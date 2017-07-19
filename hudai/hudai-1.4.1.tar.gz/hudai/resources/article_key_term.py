from hudai.resource import Resource
from pydash import pick


class ArticleKeyTermResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/article-key-terms')
        self.resource_name = 'ArticleKeyTerm'

    def list(self, params):
        return self.request({
            'params': pick(params, 'term', 'published_before', 'published_after'),
            'url': '/internal'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'term'),
            'url': '/internal'
        })

    def get(self, id):
        return self.request({
            'params': {'id': id},
            'url': '/internal/{id}'
        })

    def update(self, params):
        return self.request({
            'method': 'PUT',
            'params': pick(params, 'id'),
            'data': pick(params, 'term'),
            'url': '/internal/{id}'
        })

    def delete(self, id):
        return self.request({
            'method': 'DELETE',
            'params': {'id': id},
            'url': '/internal/{id}'
        })
