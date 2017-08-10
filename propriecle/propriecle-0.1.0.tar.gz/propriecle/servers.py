"""Maintain a local cache of Vault server details"""
import threading
import requests
from propriecle.helpers import FINISHED
from propriecle.vault import get_vault, root_client
from propriecle.conf import get_server as server_from_config
from future.utils import iteritems  # pylint: disable=E0401
import hvac.exceptions

VTHREADZ = []
VAULTZ = {}
SERVERZ = {}


def update_server(finished, server):
    """Updates our local poorly cached representation of a Vault server.
    This runs in a thread, one per Vault server. Probably needs more mutex."""
    name = server['name']
    while not finished.wait(2):
        new_s = fetch_server(VAULTZ[name], server)
        if 'cluster_id' in new_s:
            my_cluster = [x['name']
                          for _name, x
                          in iteritems(SERVERZ)
                          if x.get('cluster_id', None) == new_s['cluster_id']]
            new_s['cluster_members'] = my_cluster

        SERVERZ[name] = new_s


def get_server(name):
    """Will return the cached rerepsentation of a Vault server or if this isn't
    available will kick off a thread to start that up"""
    if name in SERVERZ:
        return SERVERZ[name]

    server = server_from_config(name)
    return start_server_thread(server)


def start_server_thread(server):
    """Starts a thread responsible for updating local info on Vault servers"""
    client = None
    name = server['name']
    if name in VAULTZ:
        client = VAULTZ[name]
    else:
        client = VAULTZ[name] = get_vault(server)

    if name in SERVERZ:
        return SERVERZ[name]

    server = SERVERZ[name] = fetch_server(client, server)
    sthread = threading.Thread(target=update_server,
                               args=(FINISHED, server,))
    VTHREADZ.append(sthread)
    sthread.setDaemon(True)
    sthread.start()
    return server


def fetch_server(client, server):
    """Fetches details from Vault, generating a complicate dict
    representing a server"""
    server_obj = {
        "name": server['name'],
        "url": server['url'],
        "client": client
    }
    if (server['name'] in SERVERZ) \
       and ('cluster_members' in SERVERZ[server['name']]):
        clustered = SERVERZ[server['name']]['cluster_members']
        server_obj['cluster_members'] = clustered

    if 'parent' in server:
        server_obj['parent'] = server['parent']

    try:
        init = client.is_initialized()
    except hvac.exceptions.InternalServerError:
        return server_obj
    except requests.ConnectionError:
        return server_obj
    except requests.ReadTimeout:
        return server_obj

    server_obj['init'] = init
    if init:
        status = client.seal_status
        server_obj['version'] = status['version']
        seal = server_obj['sealed'] = status['sealed']
        if seal:
            server_obj['unseal_required'] = status['t']
            server_obj['unseal_progress'] = status['progress']
        else:
            server_obj['cluster_name'] = status['cluster_name']
            server_obj['cluster_id'] = status['cluster_id']

            server_obj['rekey'] = False
            try:
                rekey_obj = client.rekey_status
                rekey = server_obj['rekey'] = rekey_obj['started']
                if rekey:
                    server_obj['rekey_backup'] = rekey_obj['backup']
                    server_obj['rekey_progress'] = rekey_obj['progress']
                    server_obj['rekey_required'] = rekey_obj['required']
            except hvac.exceptions.VaultDown:
                pass
            except hvac.exceptions.InternalServerError as vault_exception:
                if vault_exception.message == 'node not active but active '\
                   'node not found':
                    pass

            server_obj['ha'] = False
            try:
                leader_obj = client.read('sys/leader')
                server_obj['ha'] = leader_obj['ha_enabled']
                if leader_obj['ha_enabled']:
                    server_obj['leader'] = leader_obj['is_self']
            except hvac.exceptions.VaultDown:
                pass
            except hvac.exceptions.InternalServerError as e:
                if e.message == 'node not active but active node not found':
                    pass

            if not server_obj['ha'] or \
               (server_obj['ha'] and server_obj['leader']):
                try:
                    regen_obj = client.read('sys/generate-root/attempt')
                    server_obj['regenerating'] = regen_obj['started']
                    if server_obj['regenerating']:
                        server_obj['regen_progress'] = regen_obj['progress']
                        server_obj['regen_required'] = regen_obj['required']
                except hvac.exceptions.VaultDown:
                    pass
                except hvac.exceptions.InternalServerError as e:
                    if e.message == 'node not active but ' \
                       'active node not found':
                        pass

            client = root_client(server_obj)
            server_obj['is_root'] = False
            if client:
                try:
                    key_obj = client.key_status
                    server_obj['key_term'] = key_obj['term']
                    server_obj['is_root'] = True
                except hvac.exceptions.VaultDown:
                    pass
                except hvac.exceptions.InternalServerError as e:
                    if e.message == 'node not active but active '\
                       'node not found':
                        pass

    return server_obj
