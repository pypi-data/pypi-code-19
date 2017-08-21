"""
hudai.resources.user_digest_subscription
"""
from ..helpers.resource import Resource


class UserDigestSubscriptionResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/users/{user_id}/digest-subscriptions')
        self.resource_name = 'UserDigestSubscription'

    def list(self, user_id, day_of_week=None, iso_hour=None, page=None):
        query_params = self._set_limit_offset({
            'day_of_week': day_of_week,
            'iso_hour': iso_hour,
            'page': page
        })

        return self.http_get('/',
                             params={'user_id': user_id},
                             query_params=query_params)

    def create(self, user_id, day_of_week=None, iso_hour=None):
        return self.http_post('/',
                              params={'user_id': user_id},
                              data={'day_of_week': day_of_week,
                                    'iso_hour': iso_hour})

    def fetch(self, user_id, digest_id):
        return self.http_get('/{id}',
                             params={'user_id': user_id, 'id': digest_id})

    def delete(self, user_id, digest_id):
        return self.http_delete('/{id}',
                                params={'user_id': user_id, 'id': digest_id})
