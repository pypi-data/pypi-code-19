from ..resource import Resource


class UserResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/users')
        self.resource_name = 'User'


    # Core CRUD Actions


    def list(self, email=None):
        return self._list(email=email)

    def create(self, email=None, name=None):
        return self._create(email=email, name=name)

    def get(self, id):
        return self._get(id)

    def update(self, id, email=None, name=None):
        return self._update(id, email=email, name=name)

    def delete(self, id):
        return self._delete(id)


    # Convenience management of their followed KeyTerms


    def followed_terms_list(self, id):
        return self.get('/{id}/followed-terms',
                        params={'id': id})

    def followed_terms_add(self, id, term):
        return self.post('/{id}/followed-terms',
                         params={'id': id},
                         data={'term': term})

    def followed_terms_remove(self, id, term):
        return self.delete('/{id}/followed-terms/{term}',
                           params={'id': id, 'term': term})


    # Convenience management of their followed Companies


    def followed_companies_list(self, id):
        return self.get('/{id}/followed-companies', params={'id': id})

    def followed_companies_add(self, id, company_id):
        return self.post('/{id}/followed-companies',
                         params={'id': id},
                         data={'company_id': company_id})

    def followed_companies_remove(self, user_id, company_id):
        return self.delete('/{user_id}/followed-companies/{company_id}',
                           params={'user_id': user_id, 'company_id': company_id})
