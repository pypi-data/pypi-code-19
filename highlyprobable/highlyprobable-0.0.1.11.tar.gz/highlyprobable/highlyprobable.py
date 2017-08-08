import logging
import os
import requests
from highlyprobable.base import format_app_name
from highlyprobable.api import Account, Application, NLP, Blueprint


logger = logging.getLogger(os.path.basename(__file__))


class HighlyProbable:
    class _API:
        pass


    _MANAGE = 'manage'

    _SCHEMA = {
        _MANAGE: {
            'account': Account,
            'apps': Application,
            'services': Blueprint,
        },
        'ai': {
            'nlp': NLP
        }
    }

    def __init__(self, secret_key):
        self._secret_key = secret_key
        self._session = requests.Session()
        self._session.headers.update({
            'Authorization': 'Token %s' % self._secret_key,
            'Content-Type': 'application/json'
        })
        self.manage = HighlyProbable._API()
        self.apps = HighlyProbable._API()
        self._build_tree()

    def _close(self):
        self._session.close()

    def _build_tree(self):
        setattr(self.manage, 'account', Account(self))
        setattr(self.manage, 'apps', Application(self))
        setattr(self.manage, 'services', Blueprint(self))

        for name, app_details in getattr(self, HighlyProbable._MANAGE).apps().data.items():
            app_name = format_app_name(name)
            setattr(self.apps, app_name, HighlyProbable._API())
            setattr(getattr(self.apps, app_name), 'ai', HighlyProbable._API())
            setattr(getattr(getattr(self.apps, app_name), 'ai'), 'nlp', NLP(self, app_details))





























