import logging
import re
from urllib import parse

import flask
import requests
import requests.auth
import sepiida.context
import sepiida.errors
import sepiida.session

LOGGER = logging.getLogger(__name__)

def user_session(username=None, password=None, session=None, user=None):
    if not any([username, password, session, user]):
        if flask.has_request_context():
            credentials = sepiida.context.extract_credentials(flask.request)
            password    = credentials['password']
            session     = credentials['session']
            user        = credentials['user']
            username    = credentials['username']
        elif sepiida.backend.has_task_context():
            credentials = sepiida.backend.task_credentials()
            password    = credentials['password']
            session     = credentials['session']
            user        = credentials['user']
            username    = credentials['username']
        else:
            msg = ("You have attempted to create a user session without having a flask request context or a backend task context. "
                   "You must therefore supply your own credentials as parameters")
            raise Exception(msg)

    _user_session = requests.Session()
    if username and password:
        LOGGER.debug("Using credentials %s %s for user session", username, password)
        _user_session.auth = requests.auth.HTTPBasicAuth(username, password)
    elif session:
        LOGGER.debug("Passing through session token")
        _user_session.cookies['session'] = session
    else:
        LOGGER.warning("User session requested, but I have no session data to use")
    _user_session.headers.update({'Request-ID': sepiida.session.current_request_id()})
    return _user_session

class PrivilegedAuth(requests.auth.HTTPBasicAuth):
    def __call__(self, prepared_request):
        prepared_request = super(self.__class__, self).__call__(prepared_request)
        parts = parse.urlsplit(prepared_request.url)
        domains = flask.current_app.config.get('SEPIIDA_INTERNAL_DOMAINS', [])
        domains = '|'.join([re.escape(domain) for domain in domains])
        domains_regex = r'(.*)?\.({0})$'.format(domains)
        if not parts.scheme == 'https':
            raise InvalidPrivilegedScheme()
        if not re.fullmatch(domains_regex, parts.netloc):
            raise InvalidPrivilegedDomain()

        return prepared_request

def privileged_session(api_token=None):
    if not api_token:
        api_token = flask.current_app.config['API_TOKEN']

    _session = requests.Session()
    _session.auth = PrivilegedAuth('api', api_token)
    _session.headers.update({'Request-ID': sepiida.session.current_request_id()})
    return _session

class InvalidPrivilegedDomain(sepiida.errors.Error):
    def __init__(self):
        super(
            self.__class__,
            self,
        ).__init__(
            "Privileged domain must be trusted",
            "invalid-privileged-domain"
        )

class InvalidPrivilegedScheme(sepiida.errors.Error):
    def __init__(self):
        super(
            self.__class__,
            self,
        ).__init__(
            "Privileged request requires https",
            "invalid-privileged-sheme"
        )
