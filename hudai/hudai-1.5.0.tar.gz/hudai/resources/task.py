from hudai.resource import Resource
from pydash import pick


class TaskResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/tasks')
        self.resource_name = 'Task'

    def get(self, uuid):
        return self.request({
            'method': 'GET',
            'params': {'uuid': uuid},
            'url': '/internal/{uuid}'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'uuid'),
            'url': '/internal'
        })

    def delete(self, uuid):
        return self.request({
            'method': 'DELETE',
            'params': {'uuid': uuid},
            'url': '/internal/{uuid}'
        })
