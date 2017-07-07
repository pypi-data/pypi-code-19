"""Unility functions for negotiator2."""

from .negotiator import AcceptParameters, ContentType, ContentNegotiator
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.WARN)

def conneg_on_accept(supported_types, accept_header, default=True):
    """Do content negotiation on content type only.

    Arguments:

    supported_types - List of one or more server supported types given
        in order of server preference. The first is the default type.

    accept_header - Client provided HTTP Accept header (may be empty
        or None).                                          

    Return:

    mimetype - Best match to client preference or default type.                                                                                    
    """
    default_type = supported_types[0]
    try:
        if (accept_header is None or accept_header == ''):
            return(default_type)
        default_params = AcceptParameters(ContentType(default_type))
        acceptable = []
        for t in supported_types:
            acceptable.append(AcceptParameters(ContentType(t)))
        cn = ContentNegotiator(default_params, acceptable)
        acceptable = cn.negotiate(accept=accept_header)
        if (acceptable is not None):
            return(acceptable.content_type.mimetype())
    except Exception as e:
        logging.debug("conneg_on_accept: Ignored: " + str(e))
    return(default_type)
