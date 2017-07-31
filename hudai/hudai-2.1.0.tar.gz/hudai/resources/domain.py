from ..resource import Resource


class DomainResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/domains')
        self.resource_name = 'Domain'

    def list(self, company_id=None, hostname=None):
        return self._list(company_id=company_id, hostname=hostname)

    def create(self, company_id=None, hostname=None):
        return self._create(company_id=company_id, hostname=hostname)

    def get(self, id):
        return self._get(id)

    def update(self, id, company_id=None, hostname=None):
        return self._update(id, company_id=company_id, hostname=hostname)

    def delete(self, id):
        return self._delete(id)
