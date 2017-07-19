from hudai.resource import Resource
from pydash import pick


class KeyTermResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/key-terms')
        self.resource_name = 'KeyTerm'


    def list(self, params):
        return self.request({
            'params': pick(params, 'term', 'company_id', 'user_id'),
            'url': '/internal'
        })


    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'term', 'company_id', 'user_id'),
            'url': '/internal'
        })


    def get(self, id):
        return self.request({
            'params': {'id': id},
            'url': '/internal/{id}'
        })


    def delete(self, id):
        return self.request({
            'method': 'DELETE',
            'params': {'id': id},
            'url': '/internal/{id}'
        })
