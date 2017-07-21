from base64 import urlsafe_b64decode
from django.conf import settings
import json
import jwt
import requests
from urllib import urlencode


DOMAIN = getattr(settings, 'AUTH0_DOMAIN')
SCOPE = getattr(settings, 'AUTH0_SCOPE', 'openid email')
CLIENT_ID = getattr(settings, 'AUTH0_CLIENT_ID')
CLIENT_SECRET = getattr(settings, 'AUTH0_CLIENT_SECRET')


def get_login_url(domain=DOMAIN, scope=SCOPE, client_id=CLIENT_ID, redirect_uri=None, response_mode='form_post', state=None):
    param_dict = {
        'response_type': 'token',
        'response_mode': response_mode,
        'scope': scope,
        'client_id': client_id,
    }
    if redirect_uri is not None:
        param_dict['redirect_uri'] = redirect_uri
    if state is not None:
        param_dict['state'] = state
    params = urlencode(param_dict)
    return 'https://{domain}/authorize?{params}'.format(
        domain=domain,
        params=params,
    )


def get_logout_url(redirect_uri, client_id=CLIENT_ID, domain=DOMAIN):
    params = urlencode({
        'returnTo': redirect_uri,
        'client_id': client_id,
    })
    return 'https://{domain}/v2/logout?{params}'.format(
        domain=domain,
        params=params,
    )


def get_email_from_token(token=None, key=urlsafe_b64decode(CLIENT_SECRET), audience=CLIENT_ID):
    try:
        payload = jwt.decode(token, key=key, audience=audience, leeway=300)
        if 'email' in payload:
            return payload['email']
        elif 'sub' in payload:
            return payload['sub'].split('|').pop()
    except (jwt.InvalidTokenError, IndexError) as e:
        pass

    return None


def is_email_verified_from_token(token=None, key=urlsafe_b64decode(CLIENT_SECRET), audience=CLIENT_ID):
    try:
        payload = jwt.decode(token, key=key, audience=audience, leeway=300)
        return payload.get('email_verified', True)
    except (jwt.InvalidTokenError, IndexError) as e:
        pass

    return None
