from collections import OrderedDict
from hashlib import md5
import requests

def calculate_md5(data):
    checksum = ''
    key = 'secret' # Make sure
    for k,v in data.items():
        # print(f'md5: {v}')
        checksum = '%s%s' % (checksum,v)
    checksum = '%s%s' % (checksum,key) # add key to checksum value
    md5_hash = md5(checksum.encode('utf-8')).hexdigest()
    return md5_hash

def post_payment(data):
    url = data.pop('url')
    response = requests.post(url, data=data)
    dict_ = OrderedDict()
    new = response.text.split('&')
    for item in new:
        list_ = item.split('=')
        key = list_[0]
        value = list_[1]
        dict_[key] = value
    
    is_equal, dict_['CHECKSUM'] = validate_checksum(dict_)
    return is_equal, dict_


def validate_checksum(data):
    hash_ = data.pop('CHECKSUM')
    new_hash = calculate_md5(data)
    return hash_ == new_hash, new_hash