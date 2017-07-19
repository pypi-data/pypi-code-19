from hudai.resource import Resource
from pydash import pick


class TextCorpusResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/text-corpora')
        self.resource_name = 'TextCorpus'

    def get(self, id):
        return self.request({
            'method': 'GET',
            'params': {'id': id},
            'url': '/internal/{id}'
        })

    def list(self, params):
        return self.request({
            'method': 'GET',
            'params': pick(params, 'user_id', 'type'),
            'url': '/internal'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'user_id', 'type', 'body'),
            'url': '/internal'
        })

    def update(self, params):
        return self.request({
            'method': 'PUT',
            'data': pick(params, 'user_id', 'type', 'body'),
            'params': pick(params, 'id'),
            'url': '/internal/{id}'
        })

    def delete(self, id):
        return self.request({
            'method': 'DELETE',
            'params': {'id': id},
            'url': '/internal/{id}'
        })
