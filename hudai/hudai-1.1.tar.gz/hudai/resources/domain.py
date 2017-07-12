from hudai.resource import Resource
from pydash import pick


class DomainResource(Resource):
    def __init__(self, secret_key):
        Resource.__init__(self, secret_key)
        self.resource_name = 'Domain'

    def get(self, domain):
        return self.make_request({
            'method': 'GET',
            'params': {'domain': domain},
            'url': '/domains/internal/{domain}'
        })

    def search(self, params):
        return self.make_request({
            'method': 'GET',
            'params': pick(params, 'company_id'),
            'url': '/domains/internal'
        })

    def create(self, params):
        return self.make_request({
            'method': 'POST',
            'data': pick(params, 'domain', 'company_id'),
            'url': '/domains/internal'
        })

    def update(self, params):
        return self.make_request({
            'method': 'PUT',
            'data': pick(params, 'company_id'),
            'params': pick(params, 'domain'),
            'url': '/domains/internal/{domain}'
        })

    def delete(self, domain):
        return self.make_request({
            'method': 'DELETE',
            'params': {'domain': domain},
            'url': '/domains/internal/{domain}'
        })
