"""CLI Entrypoint"""

import os
import sys
from getpass import getpass
import logging
import cryptorito
from propriecle import gui
from propriecle.helpers import problems, do_write
from propriecle.servers import get_server
from propriecle.vault import unseal, init, seal, step_down, rekey_start, \
    rekey_enter, rekey_cancel, regenerate_start, regenerate_enter, \
    regenerate_cancel
from propriecle.keys import list_keys, get_root_token, grok_keys
from propriecle.filez import root_file_name, unseal_file_name
import propriecle.conf as conf
LOG = logging.getLogger(__name__)

def cli_root(name):
    """Prints the decrypted root token to stdout"""
    root = get_root_token(get_server(name))
    if root:
        print(root)
    else:
        problems("Root token unavailable")


def cli_unseal(name):
    """Attempts to submit every available unseal key to
    the specified Vault instance"""
    server = get_server(name)
    client = server['client']
    for key_obj in [k for k in list_keys(server) if k['key']]:
        unseal(client, key_obj['key'])


def cli_unseal_all():
    """Attempts to submit every available unseal key for each
    Vault instance in order"""

    for name in [x['name'] for x in conf.get('vaults')]:
        cli_unseal(name)


def cli_seal_all():
    """Seals every accessible Vault instance"""
    for name in [x['name'] for x in conf.get('vaults')]:
        seal(get_server(name))


def cli_init(name):
    """Initializes Vault on the specified instance"""
    server = get_server(name)
    if not init(server):
        sys.exit(1)

    sys.exit(0)


def cli_step_down(name):
    """Asks the specified Vault instance to step down from Leader"""
    step_down(get_server(name))
    sys.exit(0)


def cli_seal(name):
    """Seals the specified Vault instance"""
    if not seal(get_server(name)):
        sys.exit(1)

    sys.exit(0)


def cli_regenerate_start(name):
    """Start the root key regeneration process"""
    regenerate_start(get_server(name))


def cli_regenerate_auth(name):
    """Attempts to submit every available unseal key in support
    of the root key regeneration process"""
    server = get_server(name)
    for key_obj in [k for k in list_keys(server) if k['key']]:
        regenerate_enter(server, key_obj['key'])


def cli_regenerate_cancel(name):
    """Cancels the root key regeneration process"""
    if not regenerate_cancel(get_server(name)):
        sys.exit(1)

    sys.exit(0)


def cli_rekey_start(name):
    """Start the unseal rekey process"""
    rekey_start(get_server(name), grok_keys())


def cli_rekey_auth(name):
    """Attempts to submit every available unseal key in support
    of the unseal rekey process"""
    server = get_server(name)
    for key_obj in [k for k in list_keys(server) if k['key']]:
        rekey_enter(server, key_obj['key'])


def cli_rekey_cancel(name):
    """Cancels the unseal rekey process"""
    if not rekey_cancel(get_server(name)):
        sys.exit(1)

    sys.exit(0)


def cli_root_import(name):
    """Imports a plaintext root token and will encrypt
    according to the propriecle configuration."""
    server = get_server(name)
    root_token = getpass('Root Token: ', stream=sys.stderr)
    if not root_token:
        problems("Must specify a token")

    root_key = conf.get('root_key')
    key_id = cryptorito.key_from_keybase(root_key[8:])['fingerprint']
    encrypted = cryptorito.portable_b64encode(cryptorito.encrypt_var(root_token, [key_id]))
    do_write(encrypted, root_file_name(server))

def cli_unseal_import(name, s_slot):
    """Imports a unseal key at a spcified slot and will
    encrypt accordign to the propriecle configuration."""
    slot = int(s_slot)
    server = get_server(name)
    unseal_key = getpass('Unseal Key: ', stream=sys.stderr)
    if not unseal_key:
        problems("Must specify a unseal key")

    a_key = conf.get('keys')[slot - 1]
    key_id = cryptorito.key_from_keybase(a_key[8:])['fingerprint']
    encrypted = cryptorito.portable_b64encode(cryptorito.encrypt_var(unseal_key, [key_id]))
    do_write(encrypted, unseal_file_name(server, slot))


def main():
    """Entrypoint Actual"""
    if os.environ.get('PROPRIECLE_LOG'):
        logging.basicConfig(level=logging.DEBUG)

    root_log = logging.getLogger()
    logfile = "%s/propriecle.log" % os.environ.get('PROPRIECLE_LOG_PATH', os.getcwd())
    if os.path.exists(logfile):
        os.remove(logfile)

    file_handler = logging.FileHandler(logfile)
    if len(sys.argv) == 1:
        root_log.handlers = []
        root_log.addHandler(file_handler)
        LOG.debug("with %s handlers", len(root_log.handlers))
        gui()
    elif len(sys.argv) == 3 and sys.argv[1] == "unseal":
        cli_unseal(sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == "unseal":
        cli_unseal_all()
    elif len(sys.argv) == 3 and sys.argv[1] == "seal":
        cli_seal(sys.argv[2])
    elif len(sys.argv) == 2 and sys.argv[1] == "seal":
        cli_seal_all()
    elif len(sys.argv) == 3 and sys.argv[1] == "init":
        cli_init(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "step_down":
        cli_step_down(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "root_get":
        cli_root(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "rekey_start":
        cli_rekey_start(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "rekey_auth":
        cli_rekey_auth(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "rekey_cancel":
        cli_rekey_cancel(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "regenerate_start":
        cli_regenerate_start(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "regenerate_auth":
        cli_regenerate_auth(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "regenerate_cancel":
        cli_regenerate_cancel(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == 'root_import':
        cli_root_import(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == 'unseal_import':
        cli_unseal_import(sys.argv[2], sys.argv[3])
    else:
        sys.exit(1)
