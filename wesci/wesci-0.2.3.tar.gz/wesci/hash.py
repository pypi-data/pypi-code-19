import hashlib


class Hash(object):

    HASH_ALGO = 'sha256'
    BASE64_HASH_VERSION = 'c2hhMjU2'

    @staticmethod
    def hash(file_data):
        return '%s:%s' % (hashlib.sha256(file_data).hexdigest(),
                          Hash.BASE64_HASH_VERSION)
