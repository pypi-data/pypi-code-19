import hashlib
from bson import ObjectId
import base64


class CodeGenerator(object):

    def __init__(self):
        pass

    def shortcode(self, text):
        """
        Our main shortening function. The rationale here is that
        we are relying on the fact that for similarly sized inputs
        such as URLs the potential for collision in the 32 last bits
        of the MD5 hash is rather unlikely.

        The following things happen, in order:

        * compute the md5 digest of the given source
        * extract the lower 4 bytes
        * base64 encode the result
        * remove trailing padding if it exists

        Of course, should a collision happen, we will evict the previous
        key.

        """
        return base64.b64encode(
            hashlib.md5(text.encode()).hexdigest()[-6:]
        ).replace('=', '').replace('/', '_')

    def coupon_code(self):
        _id = ObjectId()
        code = self.shortcode(str(_id))
        code = code.upper()
        code = code.replace('I', '1')
        code = code.replace('O', '2')
        code = code.replace('0', '3')
        code = code.replace('=', '4')
        code = code.replace('+', '5')
        code = code.replace('_', '6')

        return code
