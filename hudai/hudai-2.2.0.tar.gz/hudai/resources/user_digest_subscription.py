from ..resource import Resource


class UserDigestSubscriptionResource(Resource):
    def __init__(self, client):
        Resource.__init__(self, client, base_path='/user-digest-subscription')
        self.resource_name = 'UserDigestSubscription'

    def list(self, user_id=None, day_of_week=None, iso_hour=None, page=None):
        return self._list(user_id=user_id,
                          day_of_week=day_of_week,
                          iso_hour=iso_hour,
                          page=page)

    def create(self, user_id=None, day_of_week=None, iso_hour=None):
        return self._create(user_id=user_id,
                            day_of_week=day_of_week,
                            iso_hour=iso_hour)

    def fetch(self, entity_id):
        return self._fetch(entity_id)

    def update(self, entity_id, day_of_week=None, iso_hour=None):
        return self._update(entity_id, day_of_week=day_of_week, iso_hour=iso_hour)

    def delete(self, entity_id):
        return self._delete(entity_id)
