"""Properly access secrets and stuff"""

import os
from cryptorito import decrypt_var, portable_b64decode, \
    export_gpg_key, key_from_keybase
from propriecle.filez import unseal_file_name, root_file_name
import propriecle.conf as conf
from propriecle.conf import get_server


def get_root_token(server):
    """Returns the decrypted root token. Will check both the current
    server and, failing that, other hosts in the same cluster."""
    filename = root_file_name(server)
    if not os.path.exists(filename):
        for a_server in server.get('cluster_members', []):
            a_filename = root_file_name(get_server(a_server))
            if os.path.exists(a_filename):
                return do_decrypt(a_filename)

        return None

    return do_decrypt(filename)


def list_keys(server):
    """Retuns a list of all unseal keys which are available"""
    keys = []
    index = 0
    for key in conf.get('keys'):
        key_obj = {
            'index': index,
            'name': key,
            'key': None
        }
        key_file = unseal_file_name(server, index + 1)

        if os.path.exists(key_file):
            key_obj['key'] = do_decrypt(key_file)
        else:
            for a_server in server.get('cluster_members', []):
                a_filename = unseal_file_name(a_server, index + 1)
                if os.path.exists(a_filename):
                    key_obj['key'] = do_decrypt(a_filename)
                    break

        keys.append(key_obj)
        index = index + 1

    return keys


def do_decrypt(filename):
    """GPG decrypt things in files"""
    if not os.path.exists(filename):
        return None

    handle = open(filename, 'r')
    datas = handle.read().strip()
    handle.close()
    datas_bin = portable_b64decode(datas)
    return decrypt_var(datas_bin)


def grok_key(key):
    """Extracts a single key based on ID (which may actually
    be a keybase id"""
    if key.startswith('keybase:'):
        bits = key_from_keybase(key[8:])['bundle'].split('\n')
        return ''.join(bits[3:len(bits)-2])

    return export_gpg_key(key)


def grok_keys():
    """Returns a list of all extracted keys"""
    keys = []
    for key in conf.get('keys'):
        keys.append(grok_key(key))

    return keys
