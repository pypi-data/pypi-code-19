from demands import JSONServiceClient


class ControlInterfaceApiClient(object):
    """
    Client for Control Interface Service.

    :param str auth_token:

        An access token.

    :param str api_url:
        The full URL of the API.

    """

    def __init__(self, auth_token, api_url, session=None):
        headers = {'Authorization': 'Token ' + auth_token}
        if session is None:
            session = JSONServiceClient(url=api_url,
                                        headers=headers)
        self.session = session

    def get_user_service_tokens(self, params=None):
        return self.session.get('/userservicetoken/', params=params)

    def generate_user_service_tokens(self, user):
        return self.session.post('/userservicetoken/generate/', data=user)

    def get_service(self, service):
        # return None on 404 becuase that means a service not found
        result = self.session.get('/service/%s/' % service,
                                  expected_response_codes=[404, 200])
        if "detail" in result and result["detail"] == "Not found.":
            return None
        return result

    def get_services(self, params=None):
        return self.session.get('/service/', params=params)

    def get_service_status(self, service):
        params = {"service": service, "ordering": "-created_at"}
        return self.session.get('/status/', params=params)

    def get_user_dashboards(self, user_id):
        params = {
            "user_id": user_id
        }
        return self.session.get('/userdashboard/', params=params)

    def get_dashboard(self, dashboard):
        return self.session.get('/dashboard/%s/' % dashboard)

    def get_definition_page(self, definition):
        return self.session.get('/definition/%s/' % definition)
