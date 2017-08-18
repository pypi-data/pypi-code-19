from demands import JSONServiceClient, HTTPServiceClient


class MessageSenderApiClient(object):
    """
    Client for Message Sender Service.

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

    def create_outbound(self, payload):
        return self.session.post('/outbound/', data=payload)

    def get_outbounds(self, params=None):
        return self.session.get('/outbound/', params=params)

    def create_inbound(self, payload):
        return self.session.post('/inbound/', data=payload)

    def get_inbounds(self, params=None):
        return self.session.get('/inbound/', params=params)

    def get_failed_tasks(self, params=None):
        return self.session.get('/failed-tasks/', params=params)

    def requeue_failed_tasks(self):
        return self.session.post('/failed-tasks/')
