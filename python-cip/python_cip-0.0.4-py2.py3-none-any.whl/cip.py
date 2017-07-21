import datetime
import time
import requests
from .exceptions import CIPException

import logging
logger = logging.getLogger(__name__)



class CIP:
    "Simple CIP Interface"
    def __init__(self, url, serveraddress, user=None, password=None):
        self.baseurl = url.strip("/")
        self.serveraddress = serveraddress
        self.user = user
        self.password = password

        self.session = requests.Session()


    def _url(self, url):
        return "/".join([self.baseurl, url])

    def request(self, api, *args, **kwargs):
        return self.session.post(self._url(api), *args,**kwargs)

    def do(self, api, rawdata=False, *args, **kwargs):
        logger.debug( "{0}, rawdata={1!r}, {2!r}".format(api, rawdata, kwargs) )

        r = self.session.post(self._url(api), *args,**kwargs)
        logger.debug( "{0}: status_code={1}".format(api, r.status_code) )
        if r.status_code >= 400:
            raise CIPException(r.content.decode('utf-8'))

        if rawdata:
            return r.content

        # raise  JSONDecodeError:
        reply = r.json()

        logger.debug( "{0}: reply={1!r}".format(api, reply) )
        return reply


    def login(self, user = None, password=None, catalogname=None):
        data = {
            "user" : user or self.user,
            "password" : password or self.password,
            "serveraddress" : self.serveraddress,
        }
        if catalogname is not None:
            data['catalogname'] = catalogname

        return self.do("session/open", data=data)

    def logout(self):
        self.do("session/close", rawdata=True)
        self.session.close()
