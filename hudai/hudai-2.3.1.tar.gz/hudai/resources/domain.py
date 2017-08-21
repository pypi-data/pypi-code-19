"""
hudai.resources.domain
"""
from ..helpers.resource import Resource


class DomainResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/domains')
        self.resource_name = 'Domain'

    def list(self, company_id=None, hostname=None, page=None):
        return self._list(company_id=company_id, hostname=hostname, page=page)

    def create(self, company_id=None, hostname=None):
        return self._create(company_id=company_id, hostname=hostname)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def update(self, entity_id, company_id=None, hostname=None):
        return self._update(entity_id, company_id=company_id, hostname=hostname)

    def delete(self, entity_id):
        return self._delete(entity_id)
