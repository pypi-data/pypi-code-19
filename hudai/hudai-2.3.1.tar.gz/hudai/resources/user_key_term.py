"""
hudai.resources.user_key_term
"""
from ..helpers.resource import Resource


class UserKeyTermResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/users/{user_id}/key-terms')
        self.resource_name = 'UserKeyTerm'

    def list(self, user_id, page=None):
        query_params = self._set_limit_offset({'page': page})

        return self.http_get('/', params={'user_id': user_id},
                             query_params=query_params)

    def create(self, user_id, term):
        return self.http_post('/', params={'user_id': user_id},
                              data={'term': term})

    def fetch(self, user_id, term):
        return self.http_get('/{term}',
                             params={'user_id': user_id, 'term': term})

    def delete(self, user_id, term):
        return self.http_delete('/{term}',
                                params={'user_id': user_id, 'term': term})
