import re
import datetime

from tornado.options import options
from dateutil.relativedelta import relativedelta

def utc_now():
    return datetime.datetime.utcnow()

regex = re.compile(
    r'((?P<years>\d+?)y)?((?P<months>\d+?)m)?((?P<days>\d+?)d)?((?P<hours>\d+?)hr)?((?P<minutes>\d+?)min)?'
)

def to_timestamp(dt):
    return int(dt.replace(
        tzinfo=datetime.timezone.utc).timestamp())

def parse_delta(str):
    parts = regex.match(str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in parts.items():
        if param:
            param = int(param)
            if options.sandbox:
                if name == 'hours':
                    name = 'seconds'
                    param = param * 60 * 60
                if name == 'days':
                    name = 'seconds'
                    param = param * 24 * 60 * 60
                if name == 'months':
                    name = 'seconds'
                    param = param * 30 * 24 * 60 * 60
                if name == 'years':
                    name = 'seconds'
                    param = param * 365 * 24 * 60 * 60

                p = (14400)  #  Convert 30d to 3minutes

                time_params[name] = long(float(param) / p)
            else:
                time_params[name] = param

    delta = relativedelta(**time_params)

    return delta
