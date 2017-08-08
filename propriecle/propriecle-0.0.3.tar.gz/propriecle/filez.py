"""Handle interactions with our local (hopefully) encrypted files"""
from hashlib import sha256
import propriecle.conf as conf
from propriecle.conf import get_server


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
    a_server = server
    if 'parent' in server:
        a_server = get_server(server['parent'])

    return sha256(a_server['url']).hexdigest()
