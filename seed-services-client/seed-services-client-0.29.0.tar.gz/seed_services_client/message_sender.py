from .seed_services import SeedServicesApiClient


class MessageSenderApiClient(SeedServicesApiClient):
    """
    Client for Message Sender Service.

    :param str auth_token:
        An access token.

    :param str api_url:
        The full URL of the API.

    :param JSONServiceClient session:
        An instance of JSONServiceClient to use

    """

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
