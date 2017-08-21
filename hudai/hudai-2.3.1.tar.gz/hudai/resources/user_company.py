"""
hudai.resources.user_company
"""
from ..helpers.resource import Resource


class UserCompanyResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/users-companies')
        self.resource_name = 'UserCompany'

    def list(self, user_id=None, company_id=None, page=None):
        return self._list(user_id=user_id, company_id=company_id, page=page)

    def create(self, user_id=None, company_id=None):
        return self._create(user_id=user_id, company_id=company_id)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def delete(self, entity_id):
        return self._delete(entity_id)
