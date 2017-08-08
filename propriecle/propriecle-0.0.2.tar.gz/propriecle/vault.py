"""Low level Vault interactions"""
import os
import hvac
import hvac.exceptions
from propriecle.helpers import do_write
from propriecle.filez import root_file_name, unseal_file_name
from propriecle.keys import get_root_token, grok_key, grok_keys
import propriecle.conf as conf


def init(server):
    """Initialize a fresh Vault server. It will do this based on the
    settings as defined in the proprieclerc file"""
    obj = {
        "root_token_pgp_key": grok_key(conf.get('root_key')),
        "secret_shares": len(conf.get('keys')),
        "secret_threshold": conf.get('required'),
        "pgp_keys": grok_keys()
    }
    client = server['client']
    resp = client.write('sys/init', **obj)

    if 'root_token' not in resp or \
       'keys_base64' not in resp:
        return False

    do_write(resp['root_token'], root_file_name(server))
    index = 0
    for key in resp['keys_base64']:
        do_write(key, unseal_file_name(server, index + 1))
        index = index + 1

    return True


def unseal(client, key):
    """Unseals a Vault server with the provided (decrypted) key"""
    client.unseal(key)


def seal(server):
    """Seals the Vault server. Requires the use of a root token"""
    client = root_client(server)
    if client:
        if server['leader']:
            client.seal()

        return True
    else:
        return False


def root_client(server):
    """This is like a normal Vault client but with the root token instead"""
    client = server['client']
    root_token = get_root_token(server)
    if not root_token:
        return
    else:
        setattr(client, 'token', root_token)

    if not am_root(client):
        return None

    return client


def am_root(client):
    """Determines if a vault client is root or not"""
    try:
        token = client.lookup_token()
    except hvac.exceptions.VaultDown:
        return False

    if 'data' in token and 'policies' in token['data']:
        return 'root' in token['data']['policies']

    return False


def get_vault(server):
    """Manifests an hvac Vault Client object"""
    client = hvac.Client(server['url'],
                         timeout=5,
                         verify=server.get('tls_verify', True))

    token_file = "%s/.vault-token" % os.environ['HOME']
    if 'VAULT_TOKEN' in os.environ and\
       os.environ['VAULT_TOKEN']:
        setattr(client, 'token', os.environ['VAULT_TOKEN'])
    elif os.path.exists(token_file):
        handle = open(token_file, 'r')
        setattr(client, 'token', handle.read().strip())
        handle.close()

    return client


def rekey_start(server, keys):
    """Start the rekeying process. This will result in new
    unseal keys being generated once quorum has been achieved."""
    client = server['client']
    required = conf.get('required')
    backup = conf.get('backup', False)
    client.start_rekey(secret_shares=len(keys),
                       secret_threshold=required,
                       backup=backup,
                       pgp_keys=keys)


def rotate_master(server):
    """Rotate the master key. This requires a unsealed Vault server
    and a root (or equivalent) token"""
    client = root_client(server)
    if client:
        client.rotate()
        return True

    return False


def regenerate_start(server):
    """Begin the process for regenerating the root token"""
    client = server['client']
    obj = {
        "pgp_key": grok_key(conf.get('root_key'))
    }
    client.write('sys/generate-root/attempt', **obj)


def step_down(server):
    """Ask this Vault instance to step down. Is a noop if the
    instance is already in standby"""
    client = root_client(server)
    client.write('sys/step-down')


def regenerate_enter(server, key):
    """Submit a unseal key in support of regenerating the root
    token. Returns true once the operation has completed."""
    client = server['client']

    regen_obj = client.read('sys/generate-root/attempt')
    obj = {
        'key': key,
        'nonce': regen_obj['nonce']
    }
    resp = client.write("sys/generate-root/update", **obj)
    if 'complete' not in resp:
        return False

    if resp['complete']:
        root_file = root_file_name(server)
        do_write(resp['encoded_root_token'], root_file)

    return True


def regenerate_cancel(server):
    """Cancels the regeneration of the root token"""
    client = server['client']
    client.delete('sys/generate-root/attempt')
    return True


def rekey_enter(server, key):
    """Submit a unseal key in support of rekeying the unseal keys"""
    client = server['client']
    rekey_obj = client.rekey_status
    resp = client.rekey(key, rekey_obj['nonce'])
    if 'complete' not in resp:
        return False

    if resp['complete']:
        index = 0
        for b_key in resp['keys_base64']:
            unseal_file = unseal_file_name(server, index + 1)
            do_write(b_key, unseal_file)
            index = index + 1

        return True

    return False


def rekey_cancel(server):
    """Cancel the request to rekey the unseal keys"""
    client = server['client']
    client.cancel_rekey()
    return True
