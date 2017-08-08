"""
hudai.resources.company_key_term
"""
from ..resource import Resource


class CompanyKeyTermResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/company-key-terms')
        self.resource_name = 'CompanyKeyTerm'

    def list(self, company_id=None):
        return self._list(company_id=company_id)

    def create(self, company_id=None, term=None):
        return self._create(company_id=company_id, term=term)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def delete(self, entity_id):
        return self._delete(entity_id)
