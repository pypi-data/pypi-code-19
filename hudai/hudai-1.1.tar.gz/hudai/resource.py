from os import getenv
from pydash import map_keys
from requests import Request, Session
from hudai.error import HudAiError

class Resource(object):
    def __init__(self, secret_key):
        """
        :param secret_key: API secret key
        """
        self.secret_key = secret_key

        if self.secret_key is None:
            raise HudAiError('Missing required "secretKey".', 'authentication_error')

    def make_request(self, request_config):
        """
        Abstracted request method, request config is defined in the resource itself
        :param request_config:
        :return:
        """
        base_url = getenv('HUDAI_API_BASE_URL', 'https://api.hud.ai')
        session = Session()
        req = Request(
            request_config.get('method'),
            base_url + self.build_url(request_config),
            data=request_config.get('data'),
            params=request_config.get('query')
        )
        prepared = req.prepare()
        prepared.headers['User-Agent'] = 'Hud.ai python v1.0.0 +(https://github.com/FoundryAI/hud-ai-python#readme)'
        prepared.headers['x-api-key'] = self.secret_key
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
