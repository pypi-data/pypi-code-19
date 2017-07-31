from demands import JSONServiceClient
from requests.adapters import HTTPAdapter


class SeedServicesApiClient(object):
    """
    Base API client for seed services.

    :param str auth_token:
        An access token.

    :param str api_url:
        The full URL of the API.

    :param JSONServiceClient session:
        An instance of JSONServiceClient to use

    :param retries:
        (optional) The number of times to retry an HTTP request

    """

    def __init__(self, auth_token, api_url, session=None, retries=0):
        headers = {'Authorization': 'Token ' + auth_token}
        if session is None:
            session = JSONServiceClient(url=api_url,
                                        headers=headers)
        self.session = session

        if retries > 0:
            http = HTTPAdapter(max_retries=retries)
            https = HTTPAdapter(max_retries=retries)
            self.session.mount('http://', http)
            self.session.mount('https://', https)
