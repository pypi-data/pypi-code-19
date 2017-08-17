from __future__ import unicode_literals

import re

from past.builtins import basestring


class Transformer(object):
    def __init__(self, feature):
        self.feature = feature
    
    def transform(self, data):
        return data[self.feature].apply(self.transform_datum)
    

class AreaCode(Transformer):
    """Transforms variously phone numbers into area codes
    
    e.g. "12345678901" => "234"
         "+1 (234) 567-8901" => "234"
    """

    COUNTRY_DIGITS = re.compile('^\+?1(\d{10})$')
    PUNCTUATED = re.compile('(?:1[\.\-]?)?\s?\(?(\d{3})\)?\s?[\-\.]?[\d]{3}[\-\.]?[\d]{4}')

    def transform_datum(self, datum):
        if not isinstance(datum, basestring):
            return None
        else:
            match = re.match(AreaCode.COUNTRY_DIGITS, datum)
            if match:
                return match.group(1)[0:3]

            match = re.match(AreaCode.PUNCTUATED, datum)
            if match:
                return match.group(1)
            else:
                return None


class EmailDomain(Transformer):
    """Transforms email addresses into their full domain name
    
    e.g. "bob@bob.com" => "bob.com"
    """
    NAIVE = re.compile('^[^@]+@(.+)$')

    def transform_datum(self, datum):
        if isinstance(datum, basestring):
            match = re.match(EmailDomain.NAIVE, datum)
            if match:
                return match.group(1)
        return None
