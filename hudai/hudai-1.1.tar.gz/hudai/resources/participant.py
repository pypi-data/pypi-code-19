from hudai.resource import Resource
from pydash import pick


class ParticipantResource(Resource):
    def __init__(self, secret_key):
        Resource.__init__(self, secret_key)
        self.resource_name = 'Participant'

    def get(self, id):
        return self.make_request({
            'method': 'GET',
            'params': {'id': id},
            'url': '/participants/internal/{id}'
        })

    def search(self, params):
        return self.make_request({
            'method': 'GET',
            'params': pick(params),
            'url': '/participants/internal'
        })

    def create(self, params):
        return self.make_request({
            'method': 'POST',
            'data': pick(params),
            'url': '/participants/internal'
        })

    def update(self, params):
        return self.make_request({
            'method': 'PUT',
            'data': pick(params),
            'params': pick(params, 'id'),
            'url': '/participants/internal/{id}'
        })

    def delete(self, id):
        return self.make_request({
            'method': 'DELETE',
            'params': {'participant': id},
            'url': '/participants/internal/{id}'
        })
