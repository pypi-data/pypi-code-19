from ..resource import Resource


class UserResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/users')
        self.resource_name = 'User'


    # Core CRUD Actions


    def list(self, email=None):
        return self._list(email=email)

    def create(self, email=None, name=None, time_zone=None):
        return self._create(email=email, name=name, time_zone=time_zone)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def update(self, entity_id, email=None, name=None, time_zone=None):
        return self._update(entity_id,
                            email=email,
                            name=name,
                            time_zone=time_zone)

    def delete(self, entity_id):
        return self._delete(entity_id)


    # Convenience management of their followed KeyTerms


    def followed_terms_list(self, entity_id):
        return self.http_get('/{id}/followed-terms',
                             params={'id': entity_id})

    def followed_terms_add(self, entity_id, term):
        return self.http_post('/{id}/followed-terms',
                              params={'id': entity_id},
                              data={'term': term})

    def followed_terms_remove(self, entity_id, term):
        return self.http_delete('/{id}/followed-terms/{term}',
                                params={'id': entity_id, 'term': term})


    # Convenience management of their followed Companies


    def followed_companies_list(self, entity_id):
        return self.http_get('/{id}/followed-companies',
                             params={'id': entity_id})

    def followed_companies_add(self, entity_id, company_id):
        return self.http_post('/{id}/followed-companies',
                              params={'id': entity_id},
                              data={'company_id': company_id})

    def followed_companies_remove(self, user_id, company_id):
        return self.http_delete('/{user_id}/followed-companies/{company_id}',
                                params={
                                    'user_id': user_id,
                                    'company_id': company_id
                                })
