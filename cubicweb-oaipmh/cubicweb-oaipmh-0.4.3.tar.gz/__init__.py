"""cubicweb-oaipmh application package

OAI-PMH server for CubicWeb
"""
import base64
from datetime import datetime
from collections import namedtuple

from isodate import datetime_isoformat
import pytz

from logilab.common.deprecation import deprecated


@deprecated('[oaipmh 0.2] use isodate.datetime_isoformat')
def isodate(date=None):
    if date is None:
        date = utcnow()
    return datetime_isoformat(date)


def utcnow():
    return datetime.now(tz=pytz.utc)


# Model for metadata format of records in the OAI-PMH repository.
MetadataFormat = namedtuple('MetadataFormat', ['schema', 'namespace'])


class OAIError(Exception):
    """Error in OAI-PMH request."""

    def __init__(self, errors):
        super(OAIError, self).__init__()
        self.errors = errors


class NoRecordsMatch(OAIError):
    """The combination of the values of the from, until, set and
    metadataPrefix arguments results in an empty list.
    """

    def __init__(self, msg):
        super(NoRecordsMatch, self).__init__({'noRecordsMatch': msg})


class ResumptionToken(object):
    """A resumption token represents the state information needed to continue
    a request which lead to an incomplete (paginated) response.
    """
    __slots__ = ('eid', 'setspec', 'from_date', 'until_date', 'metadata_prefix')
    _delimiter = '~'

    def __init__(self, eid, setspec=None, from_date=None, until_date=None,
                 metadata_prefix=None):
        self.eid = int(eid) if eid is not None else None
        self.setspec = setspec
        self.from_date = from_date
        self.until_date = until_date
        self.metadata_prefix = metadata_prefix

    def __str__(self):
        attrs = (getattr(self, name) for name in self.__slots__)
        return self._delimiter.join(
            (str(value) if value else '') for value in attrs)

    def __eq__(self, other):
        if not isinstance(other, ResumptionToken):
            return False
        return all(getattr(self, name) == getattr(other, name)
                   for name in self.__slots__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return self.eid is not None

    @classmethod
    def parse(cls, token=None):
        """Return a ResumptionToken parsed from `token` string."""
        if token is None:
            return cls(None)
        btoken = token.encode('ascii')  # We need bytes.
        attrs = base64.urlsafe_b64decode(btoken).split(cls._delimiter)
        parsed = dict((k, v or None) for k, v in zip(cls.__slots__, attrs))
        return cls(**parsed)

    def encode(self):
        """Return string encoding state of the resumption token."""
        if self:
            return base64.urlsafe_b64encode(str(self))


def includeme(config):
    config.include('.views')
