"""CLI Entrypoint"""

import sys
from propriecle import gui
from propriecle.helpers import problems
from propriecle.servers import get_server
from propriecle.vault import unseal, init, seal, step_down, rekey_start, \
    rekey_enter, rekey_cancel, regenerate_start, regenerate_enter, \
    regenerate_cancel
from propriecle.keys import list_keys, get_root_token, grok_keys
import propriecle.conf as conf


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


def main():
    """Entrypoint Actual"""
    if len(sys.argv) == 1:
        gui()
    elif len(sys.argv) == 3 and sys.argv[1] == "unseal":
        cli_unseal(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "seal":
        cli_seal(sys.argv[2])
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
    else:
        sys.exit(1)
