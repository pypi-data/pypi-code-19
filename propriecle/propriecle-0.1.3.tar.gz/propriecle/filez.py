"""Handle interactions with our local (hopefully) encrypted files"""
from hashlib import sha256
import logging
import propriecle.conf as conf
from propriecle.conf import get_server
LOG = logging.getLogger(__name__)

def root_file_name(server):
    """The filename of our root token"""
    filename = "%s/%s-root" % (conf.state_directory(),
                               server_hash(server))
    return filename


def unseal_file_name(server, suffix):
    """The filename of a suffixed unseal key"""
    filename = "%s/%s-unseal.%s" % (conf.state_directory(),
                                    server_hash(server),
                                    suffix)
    return filename


def server_hash(server):
    """Generate a hash of a server (or it's static parent)"""
    if not isinstance(server, dict):
        return server_hash(get_server(server))

    a_server = server
    if 'parent' in server:
        LOG.debug("has a parent %s", a_server['parent'])
        a_server = get_server(a_server['parent'])

    LOG.debug("has_server is %s", a_server)
    return sha256(a_server['url']).hexdigest()
