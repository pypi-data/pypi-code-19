"""The movements command."""


from json import dumps, loads
import requests
import datetime as dt
try:
    from urllib.parse import urlencode
except ImportError:
     from urllib import urlencode
from .base import Base
from . import utils

class Movements(Base):

    def run(self):
        token = utils.get_saved_token()
        if token == False:
            return

        params =    (  
                        ('feed',self.options["<feeds>"]),
                        ('format',"json"),
                        ('starttime', self.options["--starttime"] or (dt.datetime.utcnow() - dt.timedelta(days=1)).isoformat() + 'Z'),
                        ('endtime', self.options["--endtime"] or dt.datetime.utcnow().isoformat() + 'Z'),
                    )

        r = requests.get(self.request_url + '/b/movements?' + urlencode(params) , headers={ 'Authorization': 'JWT ' + token })
        is_expired = utils.check_if_expired(r)
        if not is_expired:
            print(dumps(loads(r.text), indent=4, sort_keys=True))
