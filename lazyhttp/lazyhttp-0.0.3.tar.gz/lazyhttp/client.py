import json
import http.server
import traceback

class RemoteException(Exception): pass

class Client(object):

    def __init__(self, server):
        self.server = server

    def req(self, url, send):
        data = {}
        try:
            with urllib.request.urlopen(self.server + url, data=json.dumps(send)) as f:
                data = json.loads(f.read().decode('utf-8'))
        except Exception as e:
            print('ERORR', e.__class__.__name__, ':', str(e))
        if 'msg' in data and 'error' in data and data['error'] is True:
            raise(RemoteException(data['msg']))
