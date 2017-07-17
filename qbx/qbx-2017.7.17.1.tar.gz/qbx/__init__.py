import json
import logging
import socket
import sys
import tempfile

import os
import requests
import asyncio
from aiohttp import web
from aiohttp.web import run_app
from docopt import docopt as docoptinit

from .haproxy import haproxy
from .pull import pull

register_kong_doc = """
Usage:
    register_kong [options]
    
Options:
    --name=<name>
    --uris=<uris>
    --port=<port>
    --ip=<ip>
    --region=<region>
"""


def register_kong(argv):
    docopt = docoptinit(register_kong_doc, argv)
    print(docopt)
    name = docopt['--name']
    uris = docopt['--uris']
    port = docopt['--port']
    region = docopt['--region']
    if region == 'alihz':
        url = 'http://alihz-master.qbtrade.org:8001/apis'
    else:
        url = 'http://kong-admin.qbtrade.org/apis'
    if not docopt['--ip']:
        ip = socket.gethostbyname(socket.gethostname())
    else:
        ip = docopt['--ip']
    requests.delete('{url}/{name}'.format(url=url, name=name))
    data = {'name': name,
            'uris': uris,
            'upstream_url': 'http://{}:{}'.format(ip, port),
            'strip_uri': 'true'
            }
    requests.post(url, data=data)
    print('register ip', ip)


watch_git_doc = """
Usage:
    watch_git.py [options] <repo> <path>
    
Options:
    --debug

"""


def watch_git(argv):
    docopt = docoptinit(watch_git_doc, argv)
    directory = tempfile.mkdtemp()
    print('watch', directory, docopt)
    os.system('cd {} && git clone {} watch'.format(directory, docopt['<repo>']))
    path = '{}/watch/{}'.format(directory, docopt['<path>'])
    with open('{}/watch/{}'.format(directory, docopt['<path>'])) as f:
        buf = f.read()
    while True:
        import time
        time.sleep(10)
        os.system('cd {}/watch && git pull'.format(directory))
        with open(path) as f:
            new = f.read()
        if new != buf:
            logging.warning('changed')
            break


watch_git_http_doc = """
Usage:
    watch_git_http.py [options] <repo> <path>

Options:
    --port=<port>
    --debug

"""


def watch_git_http(argv):
    docopt = docoptinit(watch_git_http_doc, argv)
    directory = tempfile.mkdtemp()
    print('watch', directory, docopt)
    os.system('cd {} && git clone {} watch'.format(directory, docopt['<repo>']))
    path = '{}/watch/{}'.format(directory, docopt['<path>'])
    with open('{}/watch/{}'.format(directory, docopt['<path>'])) as f:
        buf = f.read()

    def jsonify(dic, status=200):
        text = json.dumps(dic, sort_keys=True)
        return web.Response(body=text.encode('utf-8'), content_type='application/json', status=status)

    @asyncio.coroutine
    def check_repo(request):
        os.system('cd {}/watch && git pull'.format(directory))
        with open(path) as f:
            new = f.read()
        if new != buf:
            logging.warning('changed')
            return jsonify({'message': 'repo changed'}, 400)
        return jsonify({'message': 'repo not change'})

    app = web.Application()
    app.router.add_route('GET', '/watchgit', check_repo)
    run_app(app, port=int(docopt['--port']))


def run():
    print('argv---', sys.argv)
    if sys.argv[1] == 'register_kong':
        register_kong(sys.argv[2:])
    elif sys.argv[1] == 'watch_git':
        watch_git(sys.argv[2:])
    elif sys.argv[1] == 'watch_git_http':
        watch_git_http(sys.argv[2:])
    elif sys.argv[1] == 'haproxy':
        haproxy(sys.argv[2:])
    elif sys.argv[1] == 'pull':
        pull(sys.argv[2:])
    else:
        logging.warning('method not regognize')


if __name__ == '__main__':
    watch_git(['git+ssh://git@github.com/qbtrade/quantlib.git', 'log_rpc.py'])
