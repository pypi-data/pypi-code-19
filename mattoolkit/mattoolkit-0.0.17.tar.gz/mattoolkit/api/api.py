import json
from pathlib import Path
import getpass

import requests
from requests.cookies import create_cookie

CONFIG_DIR = Path('~/.config/mattoolkit/').expanduser()
CONFIG_DIR.mkdir(exist_ok=True, parents=True)


class MTKAPIError(Exception):
    def __init__(self, code, detail):
        self.code = code
        self.detail = detail


class APISession:
    TOKEN_FILENAME = CONFIG_DIR / 'token'
    API_ROOT = 'https://mtk.aves.io/api/v1.0'

    def __init__(self):
        self.session = None
        self.user = None
        self.token = None
        self._checkToken()

    def _checkToken(self):
        if self.TOKEN_FILENAME.is_file():
            data = json.load(self.TOKEN_FILENAME.open())
            self.user = data['user']
            self.token = data['token']
        self._createSession()

    def login(self):
        if self.user:
            print('Already logged into Material Toolkit')
            return

        print('Material Toolkit Login')
        username = input('| username: ')
        password = getpass.getpass('| password: ')
        response = requests.post(self.API_ROOT + '/auth', json={
            'username': username,
            'password': password
        })
        if response.status_code != 200:
            raise MTKAPIError(response.status_code, response.text)

        print('Login Successful')

        # Remove 'Bearer' and ignore " at end of token
        self.token = response.cookies['Authorization'].split()[1][:-1]
        self._createSession()

        from .user import UserResourceItem
        user = UserResourceItem(response.json()['user'])
        user.get()
        self.user = user.data
        self._saveToken(self.user, self.token)

    def logout(self):
        self._deleteToken()
        self.user = None
        self.token = None
        self.session = requests.Session()

    def _deleteToken(self):
        if self.TOKEN_FILENAME.is_file():
            self.TOKEN_FILENAME.unlink()

    def _saveToken(self, user, token):
        json.dump({'user': user, 'token': token}, self.TOKEN_FILENAME.open('w'))

    def _createSession(self):
        self.session = requests.Session()
        cookie = create_cookie('Authorization', '"Bearer %s"' % self.token)
        self.session.cookies.set_cookie(cookie)

api = APISession()
