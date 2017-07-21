import requests
import tempfile
from os import path
import json
import click

token_file_path = path.join(tempfile.gettempdir(), 'octarine_token')
try:
    with open(token_file_path, 'r') as tmp_token_file:
        token = json.load(tmp_token_file)
except FileNotFoundError:
    token = None


def refresh_token(server, port, namespace):
    global token
    url = 'http://{}:{}/ns/{}/users/{}/renew'.format(server, port, namespace, token['Id'])
    req = requests.post(url, json={'RefreshToken': token['RefreshToken']})
    if req.status_code != 200:
        raise Exception('Token refresh failed')  # change to specific exception
    token['AccessJWT'] = req.json()['AccessJWT']
    with open(token_file_path, 'w') as token_file:
        json.dump(token, token_file)


def send_request(ctx, method, urlpath, data=None):
    if not token:
        click.echo('You have to login first')
        quit()
    url = 'http://{}:{}/{}'.format(ctx.obj['creds']['Server'], ctx.obj['port'], urlpath)
    req = requests.request(method, url, json=data,
                           headers={'Authorization': 'bearer {}'.format(token['AccessJWT'])})
    if req.status_code == 401:
        refresh_token(ctx.obj['creds']['Server'], ctx.obj['creds']['port'], ctx.obj['creds']['Namespace'])
        req = requests.request(method, url, json=data,
                               headers={'Authorization': 'bearer {}'.format(token['AccessJWT'])})
    if req.status_code >= 300:
        click.echo('Failed: %s' % req.text)
        quit()
    return req
