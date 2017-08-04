# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


"""
Utility functions for AML CLI
"""

from __future__ import print_function
import os
import json
import sys
import platform
import socket
import paramiko
import threading
import errno
import uuid
import time
import tempfile
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend as crypto_default_backend
import select
from pkg_resources import working_set
from pkg_resources import resource_string

try:
    # python 3
    from urllib.request import pathname2url
    from urllib.parse import urljoin, urlparse  # pylint: disable=unused-import
    import socketserver as SocketServer
except ImportError:
    # python 2
    from urllib import pathname2url
    from urlparse import urljoin, urlparse
    import SocketServer

import subprocess
import re
import shutil
import requests
from tabulate import tabulate
from builtins import input
from azure.storage.blob import (BlobPermissions, BlockBlobService, ContentSettings)
from azure.cli.core._profile import Profile
from azure.cli.core.util import CLIError
from azure.ml.api.realtime.swagger_spec_generator import generate_service_swagger
from ._host_account_util import get_current_host_account
from ._az_util import az_login
from ._constants import SUPPORTED_RUNTIMES
from ._constants import NINJA_RUNTIMES
from ._constants import CREATE_CMD_SAMPLE
from ..ml import __version__
from azure.ml.api.realtime.services import generate_main

ice_base_url = 'https://amlacsagent.azureml-int.net'
acs_connection_timeout = 5
ice_connection_timeout = 5


# EXCEPTIONS
class InvalidConfError(Exception):
    """Exception raised when config read from file is not valid json."""
    pass


# CONTEXT CLASS
class CommandLineInterfaceContext(object):
    """
    Context object that handles interaction with shell, filesystem, and azure blobs
    """
    hdi_home_regex = r'(.*:\/\/)?(?P<cluster_name>[^\s]*)'
    aml_env_default_location = 'east us'
    az_account_name = os.environ.get('AML_STORAGE_ACCT_NAME')
    az_account_key = os.environ.get('AML_STORAGE_ACCT_KEY')
    app_insights_account_name = os.environ.get('AML_APP_INSIGHTS_NAME')
    app_insights_account_key = os.environ.get('AML_APP_INSIGHTS_KEY', '')
    acs_master_url = os.environ.get('AML_ACS_MASTER')
    acs_agent_url = os.environ.get('AML_ACS_AGENT')
    acr_home = os.environ.get('AML_ACR_HOME')
    acr_user = os.environ.get('AML_ACR_USER')
    acr_pw = os.environ.get('AML_ACR_PW')
    hdi_home = os.environ.get('AML_HDI_CLUSTER')
    base_name = os.environ.get('AML_ROOT_NAME')
    hdi_user = os.environ.get('AML_HDI_USER', '')
    hdi_pw = os.environ.get('AML_HDI_PW', '')
    model_dc_storage = os.environ.get('AML_MODEL_DC_STORAGE')
    model_dc_event_hub = os.environ.get('AML_MODEL_DC_EVENT_HUB')
    env_is_k8s = os.environ.get('AML_ACS_IS_K8S', '').lower() == 'true'
    deployment_fp = os.path.join(os.path.expanduser('~'), '.amldep')
    k8s_batch_url = os.environ.get('AML_K8S_BATCH_URL')
    k8s_realtime_url = os.environ.get('AML_K8S_REALTIME_URL')

    def __init__(self):
        self.config_path = os.path.join(get_home_dir(), '.amlconf')
        self.az_container_name = 'azureml'
        if self.hdi_home:
            outer_match_obj = re.match(self.hdi_home_regex, self.hdi_home)
            if outer_match_obj:
                self.hdi_home = outer_match_obj.group('cluster_name')
        self.hdi_domain = self.hdi_home.split('.')[0] if self.hdi_home else None
        self.forwarded_port = None

    @staticmethod
    def get_acs_ssh_private_key_path():
        """

        :return: str filepath to ssh private key
        """
        return os.path.join(os.path.expanduser('~'), '.ssh', 'acs_id_rsa')

    def set_up_mesos_port_forwarding(self):
        """

        :return: None
        """
        remote_host = self.acs_master_url
        acs_username = 'acsadmin'
        remote_port = 2200
        client = paramiko.SSHClient()
        acs_key_fp = self.get_acs_ssh_private_key_path()
        client.load_host_keys(acs_key_fp)

        # base class is silent
        client.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
        try:
            client.connect(remote_host, remote_port, username=acs_username,
                           key_filename=acs_key_fp)
        except Exception as e:
            print('*** Failed to connect to {}:{}: {}'.format(remote_host, remote_port, e))
            import traceback
            traceback.print_exc()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', 0))
        local_port = sock.getsockname()[1]
        try:
            forwarding_thread = threading.Thread(target=forward_tunnel,
                                                 args=(local_port,
                                                       '127.0.0.1',
                                                       80,
                                                       client.get_transport()))
            forwarding_thread.daemon = True
            forwarding_thread.start()
            self.forwarded_port = local_port
        except Exception as exc:
            print('Port forwarding failed: {}'.format(exc))
            raise

    @staticmethod
    def str_from_subprocess_communicate(output):
        """

        :param output: bytes or str object
        :return: str version of output
        """
        if isinstance(output, bytes):
            return output.decode('utf-8')
        return output

    def add_deployment(self, deployment_id):
        """

        :param deployment_id: str deployment id to append to deployment file
        :return: None
        """
        with open(self.deployment_fp, 'a+') as deployment_file:
            deployment_file.write('{}\n'.format(deployment_id))

    def get_deployments(self):
        """

        :return: list of  str deployment IDs
        """
        try:
            with open(self.deployment_fp) as deployment_file:
                return [deployment_id.strip() for deployment_id in deployment_file.readlines()
                        if deployment_id]
        except IOError as exc:
            # create deployment file to avoid exception in future
            if exc.errno == errno.ENOENT:
                with open(self.deployment_fp, 'w') as _:
                    pass
                return []

            # unexpected error, report
            raise CLIError('Unexpected error reading deployment file: {}. '
                           'Please contact deployml@microsoft.com if this error persists.'.format(exc))

    def remove_deployment(self, deployment_id):
        """

        :param deployment_id: str deployment id  to remove from deployment file
        :return: None
        """
        deployments = self.get_deployments()
        try:
            deployments.remove(deployment_id)
            with open(self.deployment_fp, 'w') as deployment_file:
                deployment_file.write('\n'.join(deployments))
        except ValueError:
            print('Unable to find {} among expected deployments.'.format(deployment_id))

    def run_cmd(self, cmd_list):
        """

        :param cmd: str command to run
        :return: str, str - std_out, std_err
        """
        proc = subprocess.Popen(cmd_list, shell=(not self.os_is_unix()),
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        output, err = proc.communicate()
        return self.str_from_subprocess_communicate(output), \
               self.str_from_subprocess_communicate(err)

    def read_config(self):
        """

        Tries to read in ~/.amlconf as a dictionary.
        :return: dict - if successful, the config dictionary from ~/.amlconf, None otherwise
        :raises: InvalidConfError if the configuration read is not valid json, or is not a dictionary
        """
        try:
            with open(self.config_path) as conf_file:
                conf = conf_file.read()
        except IOError:
            return None
        try:
            conf = json.loads(conf)
        except ValueError:
            raise InvalidConfError

        if not isinstance(conf, dict):
            raise InvalidConfError

        return conf

    def write_config(self, conf):
        """

        Writes out the given configuration dictionary to ~/.amlconf.
        :param conf: Configuration dictionary.
        :return: 0 if success, -1 otherwise
        """
        try:
            with open(self.config_path, 'w') as conf_file:
                conf_file.write(json.dumps(conf))
        except IOError:
            return -1

        return 0

    def in_local_mode(self):
        """
        Determines if AML CLI is running in local mode
        :return: bool - True if in local mode, false otherwise
        """

        try:
            conf = self.read_config()
            if conf and 'mode' in conf:
                return conf['mode'] == 'local'
        except InvalidConfError:
            print('Warning: Azure ML configuration file is corrupt.')
            print('Resetting to local mode.')
            self.write_config({'mode': 'local'})
            return True

        return False

    def upload_resource(self, filepath, container, asset_id):
        """

        :param filepath: str path to resource to upload
        :param container: str name of inner container to upload to
        :param asset_id: str name of asset
        :return: str location of uploaded resource
        """
        az_blob_name = '{}/{}'.format(container, asset_id)
        bbs = BlockBlobService(account_name=self.az_account_name,
                               account_key=self.az_account_key)
        bbs.create_container(self.az_container_name)
        bbs.create_blob_from_path(self.az_container_name, az_blob_name, filepath)
        return 'wasbs://{}@{}.blob.core.windows.net/' \
               '{}'.format(self.az_container_name, self.az_account_name, az_blob_name)

    def upload_dependency_to_azure_blob(self, filepath, container, asset_id,
                                        content_type='application/octet-stream'):
        """

        :param filepath: str path to resource to upload
        :param container: str name of inner container to upload to
        :param asset_id: str name of asset
        :param content_type: str content mime type
        :return: str sas url to uploaded dependency
        """
        bbs = BlockBlobService(account_name=self.az_account_name,
                               account_key=self.az_account_key)
        bbs.create_container(container)
        bbs.create_blob_from_path(container, asset_id, filepath,
                                  content_settings=ContentSettings(
                                      content_type=content_type))
        blob_sas = bbs.generate_blob_shared_access_signature(
            container_name=container,
            blob_name=asset_id,
            permission=BlobPermissions.READ,
            expiry=datetime.utcnow() + timedelta(days=30)
        )
        return 'http://{}.blob.core.windows.net/' \
               '{}/{}?{}'.format(self.az_account_name, container, asset_id, blob_sas)

    @staticmethod
    def cache_local_resource(filepath, container, asset_id):
        """

        :param filepath: str path to resource to upload
        :param container: str name of inner container to upload to
        :param asset_id: str name of asset
        :return: str location of cached resource
        """

        # create a cached version of the asset
        dest_dir = os.path.join(get_home_dir(), '.azuremlcli', container)
        if os.path.exists(dest_dir):
            if not os.path.isdir(dest_dir):
                raise ValueError('Expected asset container {} to be a directory if it'
                                 'exists'.format(dest_dir))
        else:
            try:
                os.makedirs(dest_dir)
            except OSError as exc:
                raise ValueError('Error creating asset directory {} '
                                 'for asset {}: {}'.format(dest_dir, asset_id, exc))
        dest_filepath = os.path.join(dest_dir, asset_id)
        if os.path.isfile(filepath):
            shutil.copyfile(filepath, dest_filepath)
        elif os.path.isdir(filepath):
            shutil.copytree(filepath, dest_filepath)
        else:
            raise ValueError('Assets must be a file or directory.')
        return dest_filepath

    @staticmethod
    def http_call(http_method, url, **kwargs):
        """

        :param http_method: str: (post|get|put|delete)
        :param url: str url to perform http call on
        :return: requests.response object
        """
        http_method = http_method.lower()

        # raises AttributeError if not a valid method
        return getattr(requests, http_method)(url, **kwargs)

    @staticmethod
    def get_args():
        return sys.argv

    @staticmethod
    def os_is_unix():
        return platform.system().lower() in ['linux', 'unix', 'darwin']

    @staticmethod
    def get_input(input_str):
        return input(input_str)

    @staticmethod
    def get_socket(inet, stream):
        return socket.socket(inet, stream)

    def check_call(self, cmd):
        return subprocess.check_call(cmd, shell=(not self.os_is_unix()))

    def check_output(self, cmd):
        return subprocess.check_output(cmd, shell=(not self.os_is_unix()))

    def check_marathon_port_forwarding(self):
        """

        :return: int -1 if not set up, port if set up
        """
        if not self.forwarded_port:
            self.set_up_mesos_port_forwarding()
        marathon_base_url = 'http://127.0.0.1:' + str(self.forwarded_port) + '/marathon/v2'
        marathon_info_url = marathon_base_url + '/info'
        try:
            requests.get(marathon_info_url)
        except Exception as exc:
            print('Exception: {}'.format(exc))
            raise
        return self.forwarded_port

    def get_batch_auth(self):
        """
        Get correct authorization headers
        :param context:
        :return:
        """
        if self.env_is_k8s:
            # Currently we have no Authorization around Kubernetes services
            return None
        return self.hdi_user, self.hdi_pw

    def test_aml_storage(self):
        if self.az_account_name is None or self.az_account_key is None:
            print("")
            print("Please set up your storage account for AML:")
            print("  export AML_STORAGE_ACCT_NAME=<yourstorageaccountname>")
            print("  export AML_STORAGE_ACCT_KEY=<yourstorageaccountkey>")
            print("")
            return False
        return True

    def test_aml_acr(self):
        if self.acr_home is None or self.acr_user is None or self.acr_pw is None:
            print("")
            print("Please set up your ACR registry for AML:")
            print("  export AML_ACR_HOME=<youracrdomain>")
            print("  export AML_ACR_USER=<youracrusername>")
            print("  export AML_ACR_PW=<youracrpassword>")
            print("")
            return False
        return True

    def get_amlenvrc_path(self):
        base_path = os.path.join(os.path.expanduser('~'), '.amlenvrc')
        if self.os_is_unix():
            return base_path
        else:
            return "{}.cmd".format(base_path)


def handler(chan, host, port):
    sock = socket.socket()

    try:
        sock.connect((host, port))

    except Exception as e:
        print('Forwarding request to %s:%d failed: %r' % (host, port, e))

    print ('Connected! Tunnel open %r -&gt; %r -&gt; %r' % (chan.origin_addr,
                   chan.getpeername(), (host, port)))

    while True:
        r, w, x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break

                sock.send(data)
                chan.close()

        sock.close()


class ForwardServer(SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


class Handler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            chan = self.ssh_transport.open_channel('direct-tcpip',
                                                   (self.chain_host, self.chain_port),
                                                   self.request.getpeername())
        except Exception as e:
            print('Incoming request to %s:%d failed: %s' % (self.chain_host,
                                                            self.chain_port,
                                                            repr(e)))
            return

        if chan is None:
            print('Incoming request to %s:%d was rejected by the SSH server.' %
                  (self.chain_host, self.chain_port))
            return

        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)

        chan.close()
        self.request.close()


def forward_tunnel(local_port, remote_host, remote_port, transport):
    # this is a little convoluted, but lets me configure things for the Handler
    # object.  (SocketServer doesn't give Handlers any way to access the outer
    # server normally.)
    class SubHander(Handler):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport

    ForwardServer(('', local_port), SubHander).serve_forever()


class JupyterContext(CommandLineInterfaceContext):
    def __init__(self):
        super(JupyterContext, self).__init__()
        self.local_mode = True
        self.input_response = {}

    def in_local_mode(self):
        return self.local_mode

    def set_input_response(self, prompt, response):
        self.input_response[prompt] = response

    def get_input(self, prompt):
        return self.input_response[prompt]


# UTILITY FUNCTIONS
def get_json(payload, pascal=False):
    """
    Handles decoding JSON to python objects in py2, py3
    :param payload: str/bytes json to decode
    :return: dict/list/str that represents json
    """
    if isinstance(payload, bytes):
        payload = payload.decode('utf-8')
    payload = json.loads(payload) if payload else {}
    if pascal:
        payload = to_pascal(payload)
    return payload


def get_home_dir():
    """
    Function to find home directory on windows or linux environment
    :return: str - path to home directory
    """
    return os.path.expanduser('~')


cli_context = CommandLineInterfaceContext()


def check_version(context, conf):
    """
    :param context: CommandLineInterfaceContext object
    :param conf: dict configuration dictionary
    :return: None
    """
    try:
        output, _ = context.run_cmd('pip search azuremlcli')
        installed_regex = r'INSTALLED:[\s]+(?P<current>[^\s]*)'
        latest_regex = r'LATEST:[\s]+(?P<latest>[^\s]*)'
        latest_search = re.search(latest_regex, output)
        if latest_search:
            installed_search = re.search(installed_regex, output)
            if installed_search:
                print('\033[93mYou are using AzureML CLI version {}, '
                      'but version {} is available.'.format(
                    installed_search.group('current'), latest_search.group('latest')))
                print("You should consider upgrading via the 'pip install --upgrade "
                      "azuremlcli' command.\033[0m")
                print()
        conf['next_version_check'] = (datetime.now() + timedelta(days=1)).strftime(
            '%Y-%m-%d')
        context.write_config(conf)
    except Exception as exc:
        print('Warning: Error determining if there is a newer version of AzureML CLI '
              'available: {}'.format(exc))


def first_run(context):
    """
    Determines if this is the first run (either no config file,
    or config file missing api key). In either case, it prompts
    the user to enter an api key, and validates it. If invalid,
    asks user if they want to continue and add a key at a later
    time. Also sets mode to local if this is the first run.
    Verifies version of CLI as well.
    """

    is_first_run = False
    is_config_corrupt = False
    need_version_check = False
    conf = {}

    try:
        conf = context.read_config()
        if conf:
            try:
                need_version_check = 'next_version_check' not in conf or datetime.now() > datetime.strptime(
                    conf['next_version_check'], '%Y-%m-%d')
            except ValueError:
                is_config_corrupt = True

            if need_version_check:
                check_version(context, conf)
        else:
            is_first_run = True
            conf = {}
    except InvalidConfError:
        is_config_corrupt = True

    if is_config_corrupt:
        print('Warning: Azure ML configuration file is corrupt.')

    if is_first_run or is_config_corrupt:
        conf['mode'] = 'local'
        check_version(context, conf)
        context.write_config(conf)


def get_success_and_resp_str(context, http_response, response_obj=None, verbose=False):
    """

    :param context:
    :param http_response: requests.response object
    :param response_obj: Response object to format a successful response
    :param verbose: bool - flag to increase verbosity
    :return: (bool, str) - (result, result_str)
    """
    if http_response is None:
        return False, "Response was None."
    if verbose:
        print(http_response.content)
    try:
        http_response.raise_for_status()
        json_obj = get_json(http_response.content, pascal=True)
        if response_obj is not None:
            return True, response_obj.format_successful_response(context, json_obj)
        return True, json.dumps(json_obj, indent=4, sort_keys=True)

    except ValueError:
        return True, http_response.content

    except requests.exceptions.HTTPError:
        return False, process_errors(http_response)


def process_errors(http_response):
    """

    :param http_response:
    :return: str message for parsed error
    """
    try:
        json_obj = get_json(http_response.content)
        to_print = '\n'.join(
            [detail['message'] for detail in json_obj['error']['details']])
    except (ValueError, KeyError):
        to_print = http_response.content

    return 'Failed.\nResponse code: {}\n{}'.format(http_response.status_code, to_print)


def validate_remote_filepath(context, filepath):
    """
    Throws exception if remote filepath is invalid.

    :param context: CommandLineInterfaceContext object
    :param filepath: str path to asset file. Should be http or wasb.
    :return: None
    """
    if context.in_local_mode():
        raise ValueError('Remote paths ({}) are not supported in local mode. '
                         'Please specify a local path.'.format(filepath))

    # note - wasb[s]:/// indicates to HDI cluster to use default storage backing
    if filepath.startswith('wasb:///') or filepath.startswith('wasbs:///'):
        return
    http_regex = r'https?://(?P<storage_acct>[^\.]+)\.blob\.core\.windows\.net'
    wasb_regex = r'wasbs?://[^@]+@(?P<storage_acct>[^\.]+)\.blob\.core\.windows\.net'
    for regex in (http_regex, wasb_regex):
        match_obj = re.match(regex, filepath)
        if match_obj and match_obj.group('storage_acct') == context.az_account_name:
            return

    raise ValueError('Remote paths ({}) must be on the backing '
                     'storage ({})'.format(filepath, context.az_account_name))


def update_asset_path(context, verbose, filepath, container, is_input=True):
    """

    :param context: CommandLineInterfaceContext object
    :param verbose: bool True => Debug messages
    :param filepath: str path to asset file. Can be http, wasb, or local file
    :param container: str name of the container to upload to (azureml/$(container)/assetID)
    :param is_input: bool True if asset will be used as an input
    :return: (str, str) (asset_id, location)
    """

    asset_id = os.path.split(filepath)[1]

    if filepath.startswith('http') or filepath.startswith('wasb'):
        validate_remote_filepath(context, filepath)

        # return remote resources as is
        return asset_id, filepath

    # convert relative paths
    filepath = os.path.abspath(os.path.expanduser(filepath))

    # verify that file exists
    if is_input and not os.path.exists(filepath):
        raise ValueError('{} does not exist or is not accessible'.format(filepath))

    if context.in_local_mode():
        if is_input:
            filepath = context.cache_local_resource(filepath, container, asset_id)

        return asset_id, urljoin('file:', pathname2url(filepath))

    if not is_input:
        raise ValueError('Local output paths ({}) are not supported in remote mode. '
                         'Please use a https or wasbs path on the backing '
                         'storage ({})'.format(filepath, context.az_account_name))

    if verbose:
        print('filepath: {}'.format(filepath))
        print('container: {}'.format(container))

    if os.path.isfile(filepath):
        return upload_resource(context, filepath, container, asset_id, verbose)
    elif os.path.isdir(filepath):
        return upload_directory(context, filepath, container, verbose)

    raise ValueError('Resource uploads are only supported for files and directories.')


def upload_directory(context, filepath, container, verbose):
    """

    :param context: CommandLineInterfaceContext object
    :param filepath: str path to directory to upload
    :param container: str name of container to upload to
    :param verbose: bool flag to increase verbosity
    :return: (str, str) (asset_id, location)
    """
    wasb_path = None
    to_strip = os.path.split(filepath)[0]

    for dirpath, _, files in os.walk(filepath):
        for walk_fp in files:
            to_upload = os.path.join(dirpath, walk_fp)
            container_for_upload = '{}/{}'.format(container, to_upload[
                                                             len(to_strip) + 1:-(
                                                             len(walk_fp) + 1)].replace(
                '\\', '/'))
            _, wasb_path = upload_resource(context, to_upload, container_for_upload,
                                           walk_fp,
                                           verbose)

    if wasb_path is None:
        raise ValueError('Directory {} was empty.'.format(filepath))

    asset_id = os.path.basename(filepath)
    match_obj = re.match(r'(?P<wasb_path>.*{})'.format(os.path.basename(filepath)),
                         wasb_path)
    if match_obj:
        return asset_id, match_obj.group('wasb_path')
    raise ValueError('Unable to parse upload location.')


def upload_resource(context, filepath, container, asset_id, verbose):
    """
    Function to upload local resource to blob storage
    :param context: CommandLineInterfaceContext object
    :param filepath: str path of file to upload
    :param container: str name of subcontainer inside azureml container
    :param asset_id: str name of asset inside subcontainer
    :param verbose: bool verbosity flag
    :return: str, str : uploaded asset id, blob location
    """
    wasb_package_location = context.upload_resource(filepath, container, asset_id)
    if verbose:
        print("Asset {} uploaded to {}".format(filepath, wasb_package_location))
    return asset_id, wasb_package_location


def traverse_json(json_obj, traversal_tuple):
    """
        Example:
            {
                "ID": "12345",
                "Properties" {
                    "Name": "a_service"
                }
            }

            If we wanted the "Name" property of the above json to be displayed, we would use the traversal_tuple
                ("Properties", "Name")

        NOTE that list traversal is not supported here, but can work in the case that
        a valid numerical index is passed in the tuple

    :param json_obj: json_obj to traverse. nested dictionaries--lists not supported
    :param traversal_tuple: tuple of keys to traverse the json dict
    :return: string value to display
    """
    trav = to_pascal(json_obj)
    for key in traversal_tuple:
        trav = trav[key]
    return trav


class Response(object):  # pylint: disable=too-few-public-methods
    """
    Interface for use constructing response strings from json object for successful requests
    """

    def format_successful_response(self, context, json_obj):
        """

        :param context:
        :param json_obj: json object from successful response
        :return: str response to print to user
        """
        raise NotImplementedError('Class does not implement format_successful_response')


class StaticStringResponse(Response):  # pylint: disable=too-few-public-methods
    """
    Class for use constructing responses that are a static string for successful requests.
    """

    def __init__(self, static_string):
        self.static_string = static_string

    def format_successful_response(self, context, json_obj):
        """

        :param context:
        :param json_obj: json object from successful response
        :return: str response to print to user
        """
        return self.static_string


class TableResponse(Response):
    """
    Class for use constructing response tables from json object for successful requests
    """

    def __init__(self, header_to_value_fn_dict):
        """

        :param header_to_value_fn_dict: dictionary that maps header (str) to a tuple that defines how to
        traverse the json object returned from the service
        """
        self.header_to_value_fn_dict = header_to_value_fn_dict

    def create_row(self, context, json_obj, headers):
        """

        :param json_obj: list or dict to present as table
        :param headers: list of str: headers of table
        :return:
        """
        return [self.header_to_value_fn_dict[header].set_json(json_obj).evaluate(context)
                for header in headers]

    def format_successful_response(self, context, json_obj):
        """

        :param context:
        :param json_obj: list or dict to present as table
        :return: str response to print to user
        """
        rows = []
        headers = self.header_to_value_fn_dict.keys()
        if isinstance(json_obj, list):
            for inner_obj in json_obj:
                rows.append(self.create_row(context, inner_obj, headers))
        else:
            rows.append(self.create_row(context, json_obj, headers))
        return tabulate(rows, headers=[header.upper() for header in headers],
                        tablefmt='psql')


class PaginatedTableResponse(TableResponse):
    def __init__(self, value_wrapper, header_to_value_fn_dict):
        self.value_wrapper = value_wrapper
        super(PaginatedTableResponse, self).__init__(header_to_value_fn_dict)

    def format_successful_response(self, context, json_obj):
        if isinstance(json_obj, dict) and self.value_wrapper in json_obj:
            values = json_obj[self.value_wrapper]
        else:
            values = json_obj
        return super(PaginatedTableResponse, self).format_successful_response(context, values)


class MultiTableResponse(TableResponse):
    """
    Class for use building responses with multiple tables
    """

    def __init__(self,
                 header_to_value_fn_dicts):  # pylint: disable=super-init-not-called
        """

        :param header_to_value_fn_dicts:
        """

        self.header_to_value_fn_dicts = header_to_value_fn_dicts

    def format_successful_response(self, context, json_obj):
        result = ''
        for header_to_value_fn_dict in self.header_to_value_fn_dicts:
            self.header_to_value_fn_dict = header_to_value_fn_dict
            result += super(MultiTableResponse, self).format_successful_response(context,
                                                                                 json_obj)
            result += '\n'
        return result


class StaticStringWithTableReponse(TableResponse):
    """
    Class for use constructing response that is a static string and tables from json object for successful requests
    """

    def __init__(self, static_string, header_to_value_fn_dict):
        """
        :param static_string: str that will be printed after table
        :param header_to_value_fn_dict: dictionary that maps header (str) to a tuple that defines how to
        traverse the json object returned from the service
        """
        super(StaticStringWithTableReponse, self).__init__(header_to_value_fn_dict)
        self.static_string = static_string

    def format_successful_response(self, context, json_obj):
        return '\n\n'.join([super(StaticStringWithTableReponse,
                                  self).format_successful_response(context, json_obj),
                            self.static_string])


class ValueFunction(object):
    """
    Abstract class for use finding the appropriate value for a given property in a json response.
         defines set_json, a function for storing the json response we will format
         declares evaluate, a function for retrieving the formatted string
    """

    def __init__(self):
        self.json_obj = None

    def set_json(self, json_obj):
        """

        :param json_obj: list or dict to store for processing
        :return: ValueFunction the "self" object with newly updated json_obj member
        """
        self.json_obj = json_obj
        return self

    def evaluate(self, context):
        """

        :param context:
        :return: str value to display
        """
        raise NotImplementedError("Class does not implement evaluate method.")


class TraversalFunction(ValueFunction):
    """
    ValueFunction that consumes a traversal tuple to locate the appropriate string for display
        Example:
            {
                "ID": "12345",
                "Properties" {
                    "Name": "a_service"
                }
            }

            If we wanted the "Name" property of the above json to be displayed, we would use the traversal_tuple
                ("Properties", "Name")

        NOTE that list traversal is not supported here.
    """

    def __init__(self, tup):
        super(TraversalFunction, self).__init__()
        self.traversal_tup = tup

    def evaluate(self, context):
        return traverse_json(self.json_obj, self.traversal_tup)


class ConditionalListTraversalFunction(TraversalFunction):
    """
    Class for use executing actions on members of a list that meet certain criteria
    """

    def __init__(self, tup, condition, action):
        super(ConditionalListTraversalFunction, self).__init__(tup)
        self.condition = condition
        self.action = action

    def evaluate(self, context):
        json_list = super(ConditionalListTraversalFunction, self).evaluate(context)
        return ', '.join(
            [self.action(item) for item in json_list if self.condition(item)])


def is_int(int_str):
    """

    Check whether the given variable can be cast to int
    :param int_str: the variable to check
    :return: bool
    """
    try:
        int(int_str)
        return True
    except ValueError:
        return False


def create_ssh_key_if_not_exists(context):
    from ._az_util import AzureCliError
    ssh_dir = os.path.join(os.path.expanduser('~'), '.ssh')
    private_key_path = context.get_acs_ssh_private_key_path()
    public_key_path = '{}.pub'.format(private_key_path)
    if not os.path.exists(private_key_path):
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir, 0o700)
        print('Creating ssh key {}'.format(private_key_path))
        private_key, public_key = generate_ssh_keys()
        with open(private_key_path, 'wb') as private_key_file:
            private_key_file.write(private_key)
        with open(public_key_path, 'wb') as public_key_file:
            public_key_file.write(public_key)
        os.chmod(private_key_path, 0o600)
        os.chmod(public_key_path, 0o600)
        return private_key_path, public_key.decode('ascii')

    try:
        with open(public_key_path, 'r') as sshkeyfile:
            ssh_public_key = sshkeyfile.read().rstrip()
    except IOError:
        try:
            with open(private_key_path, 'rb') as private_key_file:
                key = crypto_serialization.load_pem_private_key(
                    private_key_file.read(),
                    password=None,
                    backend=crypto_default_backend())
                ssh_public_key = key.public_key().public_bytes(
                    crypto_serialization.Encoding.OpenSSH,
                    crypto_serialization.PublicFormat.OpenSSH
                ).decode('ascii')

        except IOError:
            print('Could not load your SSH public key from {}'.format(public_key_path))
            print('Please run az ml env setup again to create a new ssh keypair.')
            raise AzureCliError('')

    return private_key_path, ssh_public_key


def generate_ssh_keys():
    key = rsa.generate_private_key(
        backend=crypto_default_backend(),
        public_exponent=65537,
        key_size=2048
    )
    private_key = key.private_bytes(
        crypto_serialization.Encoding.PEM,
        crypto_serialization.PrivateFormat.TraditionalOpenSSL,
        crypto_serialization.NoEncryption())
    public_key = key.public_key().public_bytes(
        crypto_serialization.Encoding.OpenSSH,
        crypto_serialization.PublicFormat.OpenSSH
    )
    return private_key, public_key


def to_pascal(obj):
    """ Make dictionary PascalCase """
    if isinstance(obj, dict):
        return {k[0].upper() + k[1:]: to_pascal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [to_pascal(k) for k in obj]
    return obj


def create_docker_image(score_file, dependencies, service_name, verb, target_runtime, context,
                        requirements='', schema_file='', model='', custom_ice_url='',
                        conda_file=None):
    """Create a new realtime web service."""

    temp_dir = None
    try:
        from ._k8s_util import test_acs_k8s
        from .service._realtimeutilities import upload_dependency
        verbose = verb

        is_known_runtime = target_runtime in SUPPORTED_RUNTIMES or target_runtime in NINJA_RUNTIMES
        if score_file == '' or service_name == '' or not is_known_runtime:
            print(CREATE_CMD_SAMPLE)
            return

        storage_exists = context.test_aml_storage()
        acr_exists = context.test_aml_acr()

        if context.in_local_mode():
            acs_exists = True
        elif context.env_is_k8s:
            acs_exists = test_acs_k8s()
            if not acs_exists:
                print('')
                print('Your Kubernetes cluster is not responding as expected.')
                print('Please verify it is healthy. If you set it up via `az ml env setup,` '
                      'please contact deployml@microsoft.com to troubleshoot.')
                print('')
        else:
            acs_exists = context.acs_master_url and context.acs_agent_url
            if not acs_exists:
                print("")
                print("Please set up your ACS cluster for AML:")
                print("  export AML_ACS_MASTER=<youracsmasterdomain>")
                print("  export AML_ACS_AGENT=<youracsagentdomain>")
                print("")

        if context.acr_home is None or context.acr_user is None or context.acr_pw is None:
            print("")
            print("Please set up your ACR registry for AML:")
            print("  export AML_ACR_HOME=<youracrdomain>")
            print("  export AML_ACR_USER=<youracrusername>")
            print("  export AML_ACR_PW=<youracrpassword>")
            print("")
        else:
            acr_exists = True

        if context.env_is_k8s and not re.match(r"[a-zA-Z0-9\.-]+", service_name):
            print("Kubernetes Service names may only contain alphanumeric characters, '.', and '-'")
            return

        if not storage_exists or not acs_exists or not acr_exists:
            return

        # modify json payload to update assets and driver location
        payload = resource_string(__name__, 'service/data/testrequest.json')
        json_payload = json.loads(payload.decode('ascii'))

        # update target runtime in payload
        json_payload['properties']['deploymentPackage']['targetRuntime'] = target_runtime

        # upload target storage for resources
        json_payload['properties']['storageAccount']['name'] = context.az_account_name
        json_payload['properties']['storageAccount']['key'] = context.az_account_key

        # Add dependencies

        # If there's a model specified, add it as a dependency
        if model:
            dependencies.append(model)

        # Check if user has provided a schema file for the service and if so use it to
        # generate the swagger specification for the service
        schema_arg = None
        if schema_file != '':
            schema_arg = schema_file
            dependencies.append(schema_file)
        swagger_spec = generate_service_swagger(service_name, schema_arg)

        temp_dir = tempfile.mkdtemp()
        swagger_spec_filepath = os.path.join(temp_dir, 'swagger.json')
        with open(swagger_spec_filepath, 'w') as f:
            json.dump(swagger_spec, f)
        dependencies.append(swagger_spec_filepath)

        dependency_count = 0
        if dependencies:
            print('Uploading dependencies.')
            for dependency in dependencies:
                (status, location, filename) = \
                    upload_dependency(context, dependency, verbose)
                if status < 0:
                    raise CLIError('Error resolving dependency: no such file or directory {}'.format(dependency))
                else:
                    dependency_count += 1
                    # Add the new asset to the payload
                    new_asset = {'mimeType': 'application/octet-stream',
                                 'id': filename[:32],
                                 'location': location,
                                 'unpack': status == 1}
                    json_payload['properties']['assets'].append(new_asset)
                    if verbose:
                        print("Added dependency {} to assets.".format(dependency))

        for fp, key in [(requirements, 'pipRequirements'), (conda_file, 'condaEnvFile')]:
            if fp:
                if verbose:
                    print('Uploading {} file: {}'.format(key, fp))
                (status, location, filename) = upload_dependency(context, fp, verbose)
                if status < 0:
                    print('Error resolving requirements file: no such file or directory {}'.format(fp))
                    return
                else:
                    json_payload['properties']['deploymentPackage'][key] = location

        if verbose:
            print(json.dumps(json_payload))

        # read in code file
        if os.path.isfile(score_file):
            with open(score_file, 'r') as scorefile:
                code = scorefile.read()
        else:
            print("Error: No such file {}".format(score_file))
            return

        if target_runtime == 'spark-py':
            # read in fixed preamble code
            preamble = resource_string(__name__, 'service/data/preamble').decode('ascii')

            # wasb configuration: add the configured storage account in the as a wasb location
            wasb_config = "spark.sparkContext._jsc.hadoopConfiguration().set('fs.azure.account.key." + \
                          context.az_account_name + ".blob.core.windows.net','" + context.az_account_key + "')"

            # create blob with preamble code and user function definitions from cell
            code = "{}\n{}\n{}\n\n".format(preamble, wasb_config, code)
        else:
            code = "{}\n\n".format(code)

        if verbose:
            print(code)

        az_container_name = 'amlbdpackages'
        az_blob_name = str(uuid.uuid4()) + '.py'
        bbs = BlockBlobService(account_name=context.az_account_name,
                               account_key=context.az_account_key)
        bbs.create_container(az_container_name)
        bbs.create_blob_from_text(az_container_name, az_blob_name, code,
                                  content_settings=ContentSettings(content_type='application/text'))
        blob_sas = bbs.generate_blob_shared_access_signature(
            az_container_name,
            az_blob_name,
            BlobPermissions.READ,
            datetime.utcnow() + timedelta(days=30))
        package_location = 'http://{}.blob.core.windows.net/{}/{}?{}'.format(context.az_account_name,
                                                                             az_container_name, az_blob_name, blob_sas)

        if verbose:
            print("Package uploaded to " + package_location)

        for asset in json_payload['properties']['assets']:
            if asset['id'] == 'driver_package_asset':
                if verbose:
                    print("Current driver location:", str(asset['location']))
                    print("Replacing with:", package_location)
                asset['location'] = package_location

        # modify json payload to set ACR credentials
        if verbose:
            print("Current ACR creds in payload:")
            print('location:', json_payload['properties']['registryInfo']['location'])
            print('user:', json_payload['properties']['registryInfo']['user'])
            print('password:', json_payload['properties']['registryInfo']['password'])

        json_payload['properties']['registryInfo']['location'] = context.acr_home
        json_payload['properties']['registryInfo']['user'] = context.acr_user
        json_payload['properties']['registryInfo']['password'] = context.acr_pw

        if verbose:
            print("New ACR creds in payload:")
            print('location:', json_payload['properties']['registryInfo']['location'])
            print('user:', json_payload['properties']['registryInfo']['user'])
            print('password:', json_payload['properties']['registryInfo']['password'])

        # call ICE with payload to create docker image

        # Set base ICE URL
        if custom_ice_url != '':
            base_ice_url = custom_ice_url
            if base_ice_url.endswith('/'):
                base_ice_url = base_ice_url[:-1]
        else:
            base_ice_url = 'https://eastus2euap.ice.azureml.net'

        create_url = base_ice_url + '/images/' + service_name
        get_url = base_ice_url + '/jobs'
        headers = {'Content-Type': 'application/json', 'User-Agent': 'aml-cli-{}'.format(__version__)}

        image = ''
        max_retries = 3
        try_number = 0
        while True:
            try:
                ice_put_result = requests.put(
                    create_url, headers=headers, data=json.dumps(json_payload), timeout=ice_connection_timeout)
                break
            except (requests.ConnectionError, requests.exceptions.ReadTimeout) as exc:
                if try_number < max_retries:
                    try_number += 1
                    continue
                print('Error: could not connect to Azure ML. Please try again later. If the problem persists, please contact deployml@microsoft.com') #pylint: disable=line-too-long
                print('Exception: {}'.format(exc))
                return

        if ice_put_result.status_code == 401:
            print("Invalid API key. Please update your key by running 'az ml env key -u'.")
            return
        elif ice_put_result.status_code != 201:
            print('Error connecting to Azure ML. Please contact deployml@microsoft.com with the stack below.')
            print(ice_put_result.headers)
            print(ice_put_result.content)
            return

        if verbose:
            print(ice_put_result)
        if isinstance(ice_put_result.json(), str):
            return json.dumps(ice_put_result.json())

        job_id = ice_put_result.json()['Job Id']
        if verbose:
            print('ICE URL: ' + create_url)
            print('Submitted job with id: ' + json.dumps(job_id))
        else:
            sys.stdout.write('Creating docker image.')
            sys.stdout.flush()

        job_status = requests.get(get_url + '/' + job_id, headers=headers)
        response_payload = job_status.json()
        while 'Provisioning State' in response_payload:
            job_status = requests.get(get_url + '/' + job_id, headers=headers)
            response_payload = job_status.json()
            if response_payload['Provisioning State'] == 'Running':
                time.sleep(10)
                if verbose:
                    print("Provisioning image. Details: " + response_payload['Details'])
                else:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                continue
            else:
                if response_payload['Provisioning State'] == 'Succeeded':
                    acs_payload = response_payload['ACS_PayLoad']
                    acs_payload['container']['docker']['image'] = json_payload['properties']['registryInfo']['location'] \
                                                                  + '/' + service_name
                    image = acs_payload['container']['docker']['image']
                    break
                else:
                    print('Error creating image: ' + json.dumps(response_payload))
                    return

        print('done.')
        print('Image available at : {}'.format(acs_payload['container']['docker']['image']))
        return image

    finally:
        if temp_dir is not None and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def add_sdk_to_requirements(requirements):
    # always pass sdk as dependency to mms/ICE.
    # Add the version required by the installed CLI.
    if not requirements:
        requirements = tempfile.mkstemp(suffix='.txt', prefix='requirements')[1]

    with open(requirements, 'a') as requirements_file:
        requirements_file.write('\n{}\n'.format([dist for dist in working_set.by_key[
            'azure-cli-ml'].requires() if dist.key == 'azure-ml-api-sdk'][0]))

    return requirements


def write_variables_to_amlenvrc(context, var_dict, mode='a+'):
    env_verb = 'export' if context.os_is_unix() else 'set'
    var_wrapper = "'" if context.os_is_unix() else ''
    env_statements = []
    for env_key, env_value in var_dict.items():
        env_statements.append("{0} {1}={2}{3}{2}".format(env_verb, env_key, var_wrapper, env_value))
    try:
        with open(context.get_amlenvrc_path(), mode) as env_file:
            for statement in env_statements:
                env_file.write(statement + '\n')
        print('\nYour .amlenvrc file has been updated.')
        print('Run the following commands to update your environment.')
        print("\n".join(env_statements))
        print(
            'You can also find these settings saved in {}\n'.format(context.get_amlenvrc_path()))
    except IOError:
        pass


def write_variables_to_amlenvrc_if_not_exist(context, key, value, mode='a+'):
    if os.path.exists(context.get_amlenvrc_path()):
        with open(context.get_amlenvrc_path()) as env_file:
            if key in env_file.read():
                return

    write_variables_to_amlenvrc(context, {key: value}, mode)
    

def get_sub_and_account_info():
    profile = Profile()

    try:
        subscription = profile.get_subscription()['id']
        base_url, resource_group, host_account_name = _get_hosting_account_info()
    except CLIError as exc:
        raise exc

    return base_url, subscription, resource_group, host_account_name


def _get_hosting_account_info():
    host_account = get_current_host_account()
    mms_swagger_location = urlparse(host_account['model_management_swagger_location'])
    base_url = '{}://{}'.format(mms_swagger_location.scheme, mms_swagger_location.netloc)
    resource_group = host_account['resource_group']
    host_account_name = host_account['name']

    return base_url, resource_group, host_account_name


def get_auth_token():
    az_login()
    profile = Profile()
    return profile.get_raw_token(resource=None)[0][1]


def wrap_driver_file(driver_file, schema_file, dependencies):
    """

    :param driver_file: str path to driver file
    :param schema_file: str path to schema file
    :param dependencies: list of str paths to dependencies
    :return: str path to wrapped driver file
    """
    new_driver_loc = tempfile.mkstemp(suffix='.py')[1]
    print('Creating new driver at {}'.format(new_driver_loc))
    dependencies.append(driver_file)
    return generate_main(driver_file, os.path.basename(schema_file), new_driver_loc)
