import email.utils

from .utils import to_unicode


def parse_address(addr, encoding, errors):
    if isinstance(addr, tuple):
        if len(addr) != 2:
            raise ValueError('Address tuple should have exactly two elements')
        addr_tuple = tuple(to_unicode(e, encoding, errors) for e in addr)
    elif isinstance(addr, basestring):
        addr_tuple = email.utils.parseaddr(to_unicode(addr, encoding, errors))
    else:
        raise ValueError('Email address should be a string or a tuple')
    if not addr_tuple[1]:
        raise ValueError('Invalid email address')
    return email.utils.formataddr(addr_tuple)


def parse_addresses(addr, encoding, errors):
    if not addr:
        return []
    elif isinstance(addr, tuple):
        return [parse_address(addr, encoding, errors)]
    elif isinstance(addr, basestring):
        # the provided parameter is a string
        address_tuples = email.utils.getaddresses([to_unicode(addr, encoding, errors)])
        return [email.utils.formataddr(at) for at in address_tuples]
    elif isinstance(addr, (list, set)):
        return [parse_address(a, encoding, errors) for a in addr]
    else:
        raise ValueError('addr should be a str, unicode, tuple, list or set')
