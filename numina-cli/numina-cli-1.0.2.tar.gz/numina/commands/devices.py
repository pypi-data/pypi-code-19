"""The devices command."""


from json import dumps, loads
import requests
import datetime as dt
from .base import Base
from . import utils

class Counts(Base):

    def run(self):
        token = utils.get_saved_token()
        if token == False:
            return
        
        r = requests.get(self.request_url + '/b/devices', headers={ 'Authorization': 'JWT ' + token })
        is_expired = utils.check_if_expired(r)
        if not is_expired:
            print(dumps(loads(r.text), indent=4, sort_keys=True))
