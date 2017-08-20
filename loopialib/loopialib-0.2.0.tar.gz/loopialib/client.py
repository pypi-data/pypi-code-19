from ._compat import ServerProxy, string_types
from .exceptions import LoopiaError
from .types import DnsRecord, Domain, _validate_int


def _parse_status_code(response):
    """
    Return error string code if the response is an error, otherwise ``"OK"``
    """

    # This happens when a status response is expected
    if isinstance(response, string_types):
        return response

    # This happens when a list of structs are expected
    is_single_list = isinstance(response, list) and len(response) == 1
    if is_single_list and isinstance(response[0], string_types):
        return response[0]

    # This happens when a struct of any kind is returned
    return "OK"


class Loopia(object):
    base_url = "https://api.loopia.se/RPCSERV"
    encoding = "utf-8"

    def __init__(self, user, password):
        self.user = user
        self.password = password
        self._client = ServerProxy(self.base_url, encoding=self.encoding)

    def _call(self, method, *args):
        response = getattr(self._client, method)(self.user, self.password, *args)

        # Check if there was an error with the request
        status = _parse_status_code(response)
        if status != "OK":
            raise LoopiaError.from_code(status)

        # If it's not a string and not an error we want to return the value
        if not isinstance(response, string_types):
            return response

    def get_domain(self, domain):
        """
        Return information about the given domain name.

        :param domain: Domain name to return information about
        :return: A ``Domain`` ``namedtuple``
        """

        return Domain.from_dict(self._call("getDomain", domain))

    def get_domains(self):
        """
        Return a list of all domains belonging to this account.

        :return: A ``list`` of ``Domain`` ``namedtuple``
        """

        return [
            Domain.from_dict(domain)
            for domain in self._call("getDomains")
        ]

    def get_subdomains(self, domain):
        return self._call("getSubdomains", domain)

    def remove_subdomain(self, domain, subdomain=None):
        if subdomain is None:
            subdomain = "@"

        return self._call("removeSubdomain", domain, subdomain)

    def add_zone_record(self, record, domain, subdomain=None):
        if subdomain is None:
            subdomain = "@"

        if record.id != 0:
            raise ValueError("Record must not have an ID")

        self._call("addZoneRecord", domain, subdomain, record.to_dict())

    def get_zone_records(self, domain, subdomain=None):
        if subdomain is None:
            subdomain = "@"

        return [
            DnsRecord.from_dict(record)
            for record in self._call("getZoneRecords", domain, subdomain)
        ]

    def update_zone_record(self, record, domain, subdomain=None):
        if subdomain is None:
            subdomain = "@"

        self._call("updateZoneRecord", domain, subdomain, record.to_dict())

    def remove_zone_record(self, id, domain, subdomain=None):
        """
        Remove the zone record with the given ID that belongs to the given
        domain and sub domain. If no sub domain is given the wildcard sub-domain
        is assumed.
        """

        if subdomain is None:
            subdomain = "@"

        _validate_int("id", id)

        self._call("removeZoneRecord", domain, subdomain, id)


class LoopiaTest(Loopia):
    base_url = "https://test-api.loopia.se/RPCSERV"
