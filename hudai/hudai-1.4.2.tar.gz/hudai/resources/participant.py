from hudai.resource import Resource
from pydash import pick


class ParticipantResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/participants')
        self.resource_name = 'Participant'

    def get(self, id):
        return self.request({
            'method': 'GET',
            'params': {'id': id},
            'url': '/internal/{id}'
        })

    def list(self, params):
        return self.request({
            'method': 'GET',
            'params': pick(params),
            'url': '/internal'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params),
            'url': '/internal'
        })

    def update(self, params):
        return self.request({
            'method': 'PUT',
            'data': pick(params),
            'params': pick(params, 'id'),
            'url': '/internal/{id}'
        })

    def delete(self, id):
        return self.request({
            'method': 'DELETE',
            'params': {'participant': id},
            'url': '/internal/{id}'
        })
