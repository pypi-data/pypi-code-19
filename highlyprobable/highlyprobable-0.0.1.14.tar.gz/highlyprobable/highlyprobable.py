import logging
import os
import requests
from highlyprobable.api import Account, Application, NLP, Blueprint


logger = logging.getLogger(os.path.basename(__file__))


class HighlyProbable:
    class _API:
        pass


    _MANAGE = 'manage'

    _SCHEMA = {
        _MANAGE: {
            'account': Account,
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
        setattr(self.manage, 'account', Account(self))
        setattr(self.manage, 'services', Blueprint(self))

        self.ai = None
        self._build_tree(self.ai, HighlyProbable._SCHEMA['ai'])

    def _close(self):
        self._session.close()

    def _build_tree(self, root, branch):
        for node_name, node_value in branch.items():
            setattr(root, node_name, node_value)
            if type(node_value) is str:
                self._build_tree(root[node_name], branch=branch[node_name])
        return root





























