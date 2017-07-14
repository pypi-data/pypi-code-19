from foundrybot.resource import Resource
from pydash import pick


class OrgResource(Resource):
    def __init__(self, secret_key):
        super(secret_key)
        self.resource_name = 'Org'

    def get(self, id):
        res = self.make_request({
            'method': 'GET',
            'params': {'id': id},
            'url': '/orgs/{id}'
        })
        return res.doc

    def update(self, params):
        res = self.make_request({
            'method': 'PUT',
            'params': { 'id': pick(params, 'id') },
            'data': { 'doc': pick(params, 'name') },
            'url': '/orgs/{id}'
        })
        return res.doc
