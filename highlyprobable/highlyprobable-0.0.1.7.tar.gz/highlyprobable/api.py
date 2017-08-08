import logging
import os
from uuid import uuid4
from datetime import datetime, timezone

from base import Base, Output, APIBase, format_app_name

logger = logging.getLogger(os.path.basename(__file__))


class Account(Base):
    @property
    def whoami(self):
        endpoint = self._meta_url('organizations/cli/whoami')
        return Output(self._hp._session.get(endpoint).json())


class Application(Base):
    def __call__(self, *args, **kwargs):
        return self._get

    @property
    def _get(self):
        endpoint = self._meta_url('connect/app/application')
        apps = self._hp._session.get(endpoint).json()
        _apps = dict()
        for app in apps:
            _apps[app['name']] = app
            _apps[app['name']]['available_on'] = '_hp.apps.{app_name}'.format(app_name=format_app_name(app['name']))
        return Output(_apps)

    def __repr__(self):
        return self._format(self._get.data)


    @property
    def show_all(self):
        return self._get


class Blueprint(Base):
    def __call__(self, *args, **kwargs):
        return self._get

    @property
    def _get(self):
        endpoint = self._meta_url('connect/meta/blueprint')
        blueprints = self._hp._session.get(endpoint).json()
        _blueprints = dict()
        for blueprint in blueprints:
            _blueprints[blueprint['name']] = blueprint
        return Output(_blueprints)

    def __repr__(self):
        return self._format(self._get.data)


    @property
    def show_all(self):
        return self._get


class Language(APIBase):
    def detect_language(self, text):
        '''
        This API receives a text and returns the language of the text.
        :param text: Any unicode object
        :return: A Language code
        '''
        endpoint = self._ai_url('nlp/language/detect/')
        blueprint = self._hp.manage.services.show_all.data['detect_language']
        payload = {
            'query': {
                'text': text,
            },
            'meta': {
                'account': self._hp.manage.account.whoami.data,
                'request_id': str(uuid4()),
                'auth_token': self._hp._secret_key,
                'blueprint': blueprint['url'],
                'application': self._app['url'],
                'requested_ms': int(datetime.now(timezone.utc).timestamp() * 1000),
            }
        }
        response = self._hp._session.post(endpoint, json=payload)
        return Output(response.json())


class NLP(APIBase):
    def __init__(self, highlyprobable, app):
        super().__init__(highlyprobable, app)
        self.language = Language(highlyprobable, app)
