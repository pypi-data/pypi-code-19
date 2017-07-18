from hudai.resource import Resource
from pydash import pick


class CompanyResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client)
        self.resource_name = 'Company'

    def get(self, company_id):
        return self.request({
            'method': 'GET',
            'params': {'company_id': company_id},
            'url': '/companies/internal/{company_id}'
        })

    def list(self, params):
        return self.request({
            'method': 'GET',
            'params': pick(params, 'company', 'ticket'),
            'url': '/companies/internal'
        })

    def create(self, params):
        return self.request({
            'method': 'POST',
            'data': pick(params,'company', 'ticket'),
            'url': '/companies/internal'
        })

    def update(self, params):
        return self.request({
            'method': 'PUT',
            'data': pick(params, 'company', 'ticket'),
            'params': pick(params, 'company_id'),
            'url': '/companies/internal/{company_id}'
        })

    def delete(self, company_id):
        return self.request({
            'method': 'DELETE',
            'params': {'company_id': company_id},
            'url': '/companies/internal/{company_id}'
        })
