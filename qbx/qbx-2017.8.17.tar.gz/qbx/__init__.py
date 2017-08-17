import logging
import socket
import sys

import requests
from docopt import docopt as docoptinit

from .haproxy import haproxy
from .pull import pull
from .watchgit import watch_git, watch_git_http

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


def run():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
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
