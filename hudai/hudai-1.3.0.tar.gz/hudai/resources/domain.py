from hudai.resource import Resource
from pydash import pick


class DomainResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/domains')
        self.resource_name = 'Domain'

    def get(self, domain):
        return self.request({
            'method': 'GET',
            'params': {'domain': domain},
            'url': '/internal/{domain}'
        })

    def list(self, params):
        return self.request({
            'method': 'GET',
            'params': pick(params, 'company_id'),
            'url': '/internal'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params, 'domain', 'company_id'),
            'url': '/internal'
        })

    def update(self, params):
        return self.request({
            'method': 'PUT',
            'data': pick(params, 'company_id'),
            'params': pick(params, 'domain'),
            'url': '/internal/{domain}'
        })

    def delete(self, domain):
        return self.request({
            'method': 'DELETE',
            'params': {'domain': domain},
            'url': '/internal/{domain}'
        })
