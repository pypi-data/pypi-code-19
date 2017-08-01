from ..resource import Resource


class UserCompanyResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/users-companies')
        self.resource_name = 'UserCompany'

    def list(self, user_id=None, company_id=None):
        return self._list(user_id=user_id, company_id=company_id)

    def create(self, user_id=None, company_id=None):
        return self._create(user_id=user_id, company_id=company_id)

    def get(self, id):
        return self._get(id)

    def delete(self, id):
        return self._delete(id)
