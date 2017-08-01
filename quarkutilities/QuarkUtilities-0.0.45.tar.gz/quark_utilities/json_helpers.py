import datetime
import decimal
import json

from bson import ObjectId
from bson.json_util import default


def to_json(obj, **kwargs):
    return json.dumps(obj, default=bson_to_json, **kwargs)

#: TODO delete these functions
def object_hook(json_dict):
    for (key, value) in json_dict.items():
        try:
            json_dict[key] = datetime.datetime.strptime(
                value, "%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            pass
    return json_dict


def bson_to_json(o):
    if isinstance(o, ObjectId):
        return str(o)
    if isinstance(o, datetime.datetime):
        r = o.isoformat()
        return r + 'Z'
    elif isinstance(o, datetime.date):
        return o.isoformat()
    elif isinstance(o, datetime.time):
        r = o.isoformat()
        if o.microsecond:
            r = r[:12]
        return r
    elif isinstance(o, decimal.Decimal):
        return str(o)
    return default(o)
