from hudai.resource import Resource
from pydash import pick


class UserResource(Resource):
    def __init__(self, secret_key):
        Resource.__init__(self, secret_key)
        self.resource_name = 'User'

    def get(self, id):
        return self.make_request({
            'method': 'GET',
            'params': {'id': id},
            'url': '/users/internal/{id}'
        })

    def search(self, params):
        return self.make_request({
            'method': 'GET',
            'params': pick(params, 'email', 'name'),
            'url': '/users/internal'
        })

    def create(self, params):
        return self.make_request({
            'method': 'POST',
            'data': pick(params, 'email', 'name', 'hash'),
            'url': '/users/internal'
        })

    def update(self, params):
        return self.make_request({
            'method': 'PUT',
            'data': pick(params, 'email', 'name', 'hash'),
            'params': pick(params, 'id'),
            'url': '/users/internal/{id}'
        })

    def delete(self, id):
        return self.make_request({
            'method': 'DELETE',
            'params': {'id': id},
            'url': '/users/internal/{id}'
        })
