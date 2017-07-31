from ..resource import Resource


class CompanyKeyTermResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/company-key-terms')
        self.resource_name = 'CompanyKeyTerm'

    def list(self, company_id=None):
        return self._list(company_id=company_id)

    def create(self, company_id=None, term=None):
        return self._create(company_id=company_id, term=term)

    def get(self, id):
        return self._get(id)

    def delete(self, id):
        return self._delete(id)
