from pydash import map_keys
from requests import Request, Session
from foundrybot.error import FoundrybotError

class Resource:
    def __init__(self, secret_key):
        """
        :param secret_key: API secret key
        """
        self.secret_key = secret_key

        if self.secret_key is None:
            raise FoundrybotError('Missing required "secretKey".', 'authentication_error')

    def make_request(self, request_config):
        """
        Abstracted request method, request config is defined in the resource itself
        :param request_config:
        :return:
        """
        session = Session()
        req = Request(
            request_config.method,
            'https://api.foundrybot.com/v1' + self.build_url(request_config),
            auth=(self.secret_key, ''),
            data=request_config.data,
            params=request_config.query
        )
        prepared = req.prepare()
        prepared.headers['User-Agent'] = 'Foundrybot python v1.0.0 +(https://github.com/FoundryAI/foundrybot-python#readme)'
        return session.send(prepared).json()

    def build_url(self, request_config):
        """
        Build the url path string
        :return url:
        """
        url = request_config.get('url')
        params = request_config.get('params')
        if params is not None:
            url = url.format(**params)
        return url
