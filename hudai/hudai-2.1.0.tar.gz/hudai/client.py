from datetime import date, datetime
from pydash.chaining import chain
from pydash.objects import map_keys, map_values
from pydash.strings import camel_case, snake_case
import requests

from . import __version__
from .error import HudAiError
from .resources import *

USER_AGENT = 'HUD.ai Python v{} +(https://github.com/FoundryAI/hud-ai-python#readme)'.format(__version__)

class HudAi:
    def __init__(self, api_key=None, base_url='https://api.hud.ai/v1'):
        if not api_key:
            raise HudAiError('missing api_key', 'initialization_error')

        self._api_key = api_key
        self._base_url = base_url

        self.article_highlights = ArticleHighlightsResource(self)
        self.article_key_term = ArticleKeyTermResource(self)
        self.article = ArticleResource(self)
        self.company_key_term = CompanyKeyTermResource(self)
        self.company = CompanyResource(self)
        self.domain = DomainResource(self)
        self.key_term = KeyTermResource(self)
        self.system_event = SystemEventResource(self)
        self.system_task = SystemTaskResource(self)
        self.text_corpus = TextCorpusResource(self)
        self.user_company = UserCompanyResource(self)
        self.user_digest_subscription = UserDigestSubscriptionResource(self)
        self.user_key_term = UserKeyTermResource(self)
        self.user = UserResource(self)


    def get(self, path, query_params={}):
        response = requests.get(self._build_url(path),
                                params=self._web_safe(query_params),
                                headers=self._get_headers())

        return self._pythonify(response.json())

    def post(self, path, query_params={}, data={}):
        response = requests.post(self._build_url(path),
                                 params=self._web_safe(query_params),
                                 data=self._jsonify(data),
                                 headers=self._get_headers())

        return self._pythonify(response.json())


    def put(self, path, query_params={}, data={}):
        response = requests.put(self._build_url(path),
                                params=self._web_safe(query_params),
                                data=self._jsonify(data),
                                headers=self._get_headers())

        return self._pythonify(response.json())


    def patch(self, path, query_params={}, data={}):
        response = requests.patch(self._build_url(path),
                                  params=self._web_safe(query_params),
                                  data=self._jsonify(data),
                                  headers=self._get_headers())

        return self._pythonify(response.json())


    def delete(self, path, query_params={}):
        response = requests.delete(self._build_url(path),
                                   params=self._web_safe(query_params),
                                   headers=self._get_headers())

        return self._pythonify(response.json())


    def _build_url(self, path):
        return '{}{}'.format(self._base_url, path)


    def _get_headers(self):
        return { 'User-Agent': USER_AGENT, 'x-api-key': self._api_key }


    def _jsonify(self, value):
        if type(value) is not dict:
            return self._web_safe(value)

        return chain(value) \
            .map_keys(lambda value, key: camel_case(key)) \
            .map_values(lambda value: self._jsonify(value)) \
            .value()


    def _pythonify(self, value):
        if type(value) is str:
            try:
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
            except ValueError:
                return value

        if type(value) is list:
            return [self._pythonify(item) for item in value]

        if type(value) is dict:
            return chain(value) \
                .map_keys(lambda value, key: snake_case(key)) \
                .map_values(lambda value: self._pythonify(value)) \
                .value()

        return value


    def _web_safe(self, value):
        if type(value) is datetime:
            return value.isoformat()

        if type(value) is date:
            return value.isoformat()

        if type(value) is list:
            return [self._web_safe(item) for item in value]

        if type(value) is dict:
            return map_values(value, lambda val: self._web_safe(val))

        return value
