from __future__ import unicode_literals

import base64
import datetime
import hashlib
import hmac

from requests import Session
from requests.auth import AuthBase
import six
from six.moves.urllib import parse

from . import __version__, repo_url
from .exceptions import InvalidCredentials


class BelugaAPIAuth(AuthBase):
    def __init__(self, token_id=None, token_secret=None, username=None,
                 password=None):
        super(BelugaAPIAuth, self).__init__()

        if not (token_id and token_secret) and not (username and password):
            raise InvalidCredentials('Either token ID + token secret OR '
                                     'username + password is required.')

        self.token_id = token_id
        self.token_secret = token_secret
        self.username = username
        self.password = password

    def __call__(self, r):
        if self.token_id and self.token_secret:
            url = parse.urlparse(r.url)
            if url.query:
                path_qs = '%s?%s' % (url.path, url.query)
            else:
                path_qs = url.path

            date = datetime.datetime.utcnow().isoformat()

            parts = [r.method, path_qs, date]
            if r.method in ['POST', 'PUT']:
                parts.append(hashlib.sha512(r.body).hexdigest())

            sign_string = ':'.join(parts)

            signed_hmac = hmac.new(self.token_secret.encode(),
                                   sign_string.encode(),
                                   hashlib.sha512).hexdigest()

            r.headers.update({
                'Authorization': 'Token %s %s' % (self.token_id, signed_hmac),
                'Date': date,
            })
        else:
            b64_auth = six.text_type(base64.b64encode(('%s:%s' % (
                self.username, self.password)).encode()), 'utf-8')
            r.headers['Authorization'] = 'Basic %s' % b64_auth
        return r


class BelugaAPI(Session):
    def __init__(self, token_id=None, token_secret=None, username=None,
                 password=None, base_url=None, accept=None):
        super(BelugaAPI, self).__init__()

        self.base_url = base_url or 'https://api.belugacdn.com'
        self.auth = BelugaAPIAuth(token_id, token_secret, username, password)
        self.headers = {
            'Accept': accept or 'application/json',
            'User-Agent': 'beluga_py/%s (+%s)' % (__version__, repo_url)
        }

    def request(self, method, url, *args, **kwargs):
        url_parts = parse.urlparse(url)
        if not url_parts.scheme:
            url = '/'.join([self.base_url.rstrip('/'), url.lstrip('/')])
        return super(BelugaAPI, self).request(method, url, *args, **kwargs)
