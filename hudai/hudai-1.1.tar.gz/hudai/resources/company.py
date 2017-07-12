from hudai.resource import Resource
from pydash import pick


class CompanyResource(Resource):
    def __init__(self, secret_key):
        Resource.__init__(self, secret_key)
        self.resource_name = 'Company'

    def get(self, company_id):
        return self.make_request({
            'method': 'GET',
            'params': {'company_id': company_id},
            'url': '/companies/internal/{company_id}'
        })

    def search(self, params):
        return self.make_request({
            'method': 'GET',
            'params': pick(params, 'company', 'ticket'),
            'url': '/companies/internal'
        })

    def create(self, params):
        return self.make_request({
            'method': 'POST',
            'data': pick(params,'company', 'ticket'),
            'url': '/companies/internal'
        })

    def update(self, params):
        return self.make_request({
            'method': 'PUT',
            'data': pick(params, 'company', 'ticket'),
            'params': pick(params, 'company_id'),
            'url': '/companies/internal/{company_id}'
        })

    def delete(self, company_id):
        return self.make_request({
            'method': 'DELETE',
            'params': {'company_id': company_id},
            'url': '/companies/internal/{company_id}'
        })
