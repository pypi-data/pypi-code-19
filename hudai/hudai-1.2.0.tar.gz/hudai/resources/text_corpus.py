from hudai.resource import Resource
from pydash import pick


class TextCorpusResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client)
        self.resource_name = 'TextCorpus'

    def get(self, id):
        return self.request({
            'method': 'GET',
            'params': {'id': id},
            'url': '/test-corpora/internal/{id}'
        })

    def list(self, params):
        return self.request({
            'method': 'GET',
            'params': pick(params, 'user_id', 'type'),
            'url': '/test-corpora/internal'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'user_id', 'type', 'body'),
            'url': '/test-corpora/internal'
        })

    def update(self, params):
        return self.request({
            'method': 'PUT',
            'data': pick(params, 'user_id', 'type', 'body'),
            'params': pick(params, 'id'),
            'url': '/test-corpora/internal/{id}'
        })

    def delete(self, id):
        return self.request({
            'method': 'DELETE',
            'params': {'id': id},
            'url': '/test-corpora/internal/{id}'
        })
