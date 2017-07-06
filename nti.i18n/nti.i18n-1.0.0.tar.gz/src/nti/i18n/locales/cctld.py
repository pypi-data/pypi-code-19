#!/usr/bin/env python
"""
Implementation of country-code language information.

"""

from __future__ import print_function, unicode_literals, absolute_import, division
__docformat__ = "restructuredtext en"

logger = __import__('logging').getLogger(__name__)

import json
import pkg_resources

from zope.interface import implementer
from zope.cachedescriptors.property import Lazy

from .interfaces import ICcTLDInformation


@implementer(ICcTLDInformation)
class CcTLDInformation(object):
    """
    A list of country code top level domains their relevant languages.

    Descriptions for most TLDs a can be found at
    http://en.wikipedia.org/wiki/List_of_Internet_top-level_domains
    """

    @Lazy
    def _domain_list(self):
        # Top level domain list taken from
        # http://data.iana.org/TLD/tlds-alpha-by-domain.txt
        # This is encoded in IDNA, but python fails to decode
        # when the prefix, XN--, is capitalized. That's OK, we have to
        # lower-case things anyway.
        tlds_bytes = pkg_resources.resource_string(__name__, 'tlds-alpha-by-domain.txt')
        tlds_bytes_lower = tlds_bytes.lower()
        tlds_str = tlds_bytes_lower.decode('idna')
        return tlds_str.splitlines()

    @Lazy
    def _language_map(self):
        language_bytes = pkg_resources.resource_string(__name__, 'tlds.json')
        language_str = language_bytes.decode('ascii')
        return json.loads(language_str)

    def getAvailableTLDs(self):
        return list(self._domain_list)

    def getTLDs(self):
        all_langs = {code: () for code in self._domain_list}
        all_langs.update(self._language_map)
        return all_langs

    def getLanguagesForTLD(self, tld):
        if tld in self._domain_list:
            return self._language_map.get(tld, ())
        raise KeyError(tld)
