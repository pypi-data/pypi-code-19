from demands import JSONServiceClient, HTTPServiceClient


class ServiceRatingApiClient(object):
    """
    Client for Service Rating Service.

    :param str auth_token:
        An access token.

    :param str api_url:
        The full URL of the API.

    """

    def __init__(self, auth_token, api_url, session=None, session_http=None):
        if session is None:
            session = JSONServiceClient(
                url=api_url, headers={'Authorization': 'Token ' + auth_token})

        if session_http is None:
            session_http = HTTPServiceClient(
                url=api_url, headers={'Authorization': 'Token ' + auth_token})
        self.session = session
        self.session_http = session_http

    # Invites
    def get_invites(self, params=None):
        return self.session.get('/invite/', params=params)

    def get_invite(self, invite_id):
        return self.session.get('/invite/%s/' % invite_id)

    def create_invite(self, invite):
        return self.session.post('/invite/', data=invite)

    def update_invite(self, invite_id, data=None):
        return self.session.patch('/invite/%s/' % invite_id, data=data)

    def delete_invite(self, invite_id):
        # Ratings should be deleted first for FK reasons
        self.session.delete('/invite/%s/' % invite_id)
        return {"success": True}

    # Ratings
    def get_ratings(self, params=None):
        return self.session.get('/rating/', params=params)

    def get_rating(self, rating_id):
        return self.session.get('/rating/%s/' % rating_id)

    def create_rating(self, rating):
        return self.session.post('/rating/', data=rating)

    def update_rating(self, rating_id, data=None):
        return self.session.patch('/rating/%s/' % rating_id, data=data)

    def delete_rating(self, rating_id):
        self.session.delete('/rating/%s/' % rating_id)
        return {"success": True}
