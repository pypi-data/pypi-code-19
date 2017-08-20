from collections import namedtuple
from datetime import date, datetime

from ._compat import string_types, ustr


__all__ = [
    "DnsRecord",
    "Domain",
]


_type = type
def _validate_type(name, value, type, exact_type=False):
    if exact_type:
        match = _type(value) is type
    else:
        match = isinstance(value, type)

    if not match:
        msg = "Expected '{name}' to be of type '{type}', got '{value}'"
        raise TypeError(msg.format(
            name=name,
            type=type.__name__,
            value=_type(value).__name__
        ))


def _validate_int(name, value):
    _validate_type(name, value, type=int, exact_type=True)
    if value < 0:
        raise ValueError("'{name}' must not be less than 0".format(name=name))


_record_types = frozenset([
    "A", "AAAA", "CERT", "CNAME", "HINFO", "HIP", "IPSECKEY", "LOC",
    "MX", "NAPTR", "NS", "SRV", "SSHFP", "TXT"])


def _validate_record_type(type):
    if type not in _record_types:
        raise ValueError("Type '{type}' is not either of ({types})".format(
            type=type,
            types=", ".join(_record_types)))


_DnsRecord = namedtuple("_DnsRecord", ["type", "ttl", "priority", "data", "id"])
class DnsRecord(_DnsRecord):
    def __new__(cls, type, ttl=None, priority=None, data=None, id=None):
        _validate_record_type(type)

        if ttl is None:
            ttl = 3600
        _validate_int("ttl", ttl)

        if priority is None:
            priority = 0
        _validate_int("priority", priority)

        if data is None:
            data = ""

        if id is None:
            id = 0
        _validate_int("id", id)

        return super(DnsRecord, cls).__new__(cls, type, ttl, priority, data, id)

    def _replace(self, **kwargs):
        if "type" in kwargs:
            _validate_record_type(kwargs["type"])

        for attr in ("ttl", "priority", "id"):
            if attr in kwargs:
                _validate_int(attr, kwargs[attr])

        return super(DnsRecord, self)._replace(**kwargs)

    replace = _replace

    def __repr__(self):
        return super(DnsRecord, self).__repr__().lstrip("_")

    @classmethod
    def from_dict(cls, record):
        return cls(
            type=record["type"],
            ttl=record["ttl"],
            priority=record["priority"],
            data=record["rdata"],
            id=record["record_id"])

    def to_dict(self):
        return {
            "type": self.type,
            "ttl": self.ttl,
            "priority": self.priority,
            "rdata": self.data,
            "record_id": self.id,
        }


_Domain = namedtuple("_Domain", [
    "domain",
    "expiration_date",
    "auto_renew",
    "registered",
    "paid",
    "invoice_number",
])
class Domain(_Domain):
    __slots__ = ()

    def __new__(
            cls, domain, expiration_date, auto_renew, registered, paid,
            invoice_number=None):
        _validate_type("domain", domain, type=string_types)
        _validate_type(
            "expiration_date", expiration_date, type=date, exact_type=True)
        if auto_renew is not None:
            _validate_type("auto_renew", auto_renew, type=bool)
        _validate_type("registered", registered, type=bool)
        _validate_type("paid", paid, type=bool)
        _validate_int("invoice_number", invoice_number)

        return super(Domain, cls).__new__(
            cls, domain, expiration_date, auto_renew, registered, paid,
            invoice_number)

    def __repr__(self):
        return super(Domain, self).__repr__().lstrip("_")

    @classmethod
    def from_dict(cls, record):
        return cls(
            domain=record["domain"],
            expiration_date=datetime.strptime(
                record["expiration_date"], "%Y-%m-%d").date(),
            # NOT_HANDLED_BY_LOOPIA is possible but handled as None since
            # the status is unknown
            auto_renew={
                "NORMAL": True,
                "DEACTIVATED": False,
            }.get(record["renewal_status"]),
            registered=bool(record["registered"]),
            paid=bool(record["paid"]),
            invoice_number=record["reference_no"],
        )

