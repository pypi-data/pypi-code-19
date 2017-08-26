# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import requests
from ._util import cli_context
from ._constants import SUCCESS_RETURN_CODE
from ._az_util import az_login
from ._az_util import az_check_subscription
from ._az_util import az_create_resource_group
from ._az_util import az_get_active_subscription_id
from ._compute_util import create_compute_resource
from ._compute_util import delete_compute_resource
from ._compute_util import get_compute_resource
from ._compute_util import get_current_compute_resource
from ._compute_util import get_compute_resource_keys
from ._az_util import az_register_provider
from azure.cli.core.util import CLIError
from azure.cli.core.commands import client_factory
from azure.mgmt.resource.resources import ResourceManagementClient
from msrestazure.azure_exceptions import CloudError
from ._constants import MLC_CLIENT_ENUMS_PATH
from importlib import import_module
mlc_client_enums = import_module(MLC_CLIENT_ENUMS_PATH, package=__package__)
OperationStatus = mlc_client_enums.OperationStatus

import azure.cli.core.azlogging as azlogging
logger = azlogging.get_az_logger(__name__)


def compute_create(cluster_name, service_principal_app_id, service_principal_password,
                   location, resource_group=None, agent_count=2, yes=False, cert_pem=None,
                   cert_key_pem=None, storage_arm_id=None, cert_cname=None, master_count=1,
                   context=cli_context):
    _compute_create(resource_group, cluster_name, service_principal_app_id,
                    service_principal_password, location, agent_count, yes, cert_pem,
                    cert_key_pem, storage_arm_id, cert_cname, master_count, context)

def _compute_create(resource_group, cluster_name, service_principal, client_secret,
                    location, agent_count=2, yes=False, cert_pem=None,
                    cert_key_pem=None, storage_arm_id=None, cert_cname=None, master_count=1,
                    context=cli_context):
    if location is None:
        raise CLIError('Location must be specified for cluster creation.')

    if master_count not in [1, 3, 5]:
        raise CLIError('Master count must be 1, 3, or 5.')

    # handle SSL cert
    cert_str, key_str, ssl_enabled = None, None, 'Disabled'
    if cert_pem is not None or cert_key_pem is not None or cert_cname is not None:
        if cert_key_pem is None:
            raise CLIError(
                'Certificate key file must be provided if certificate is provided.')
        if cert_pem is None:
            raise CLIError(
                'Certificate file must be provided if certificate key file is provided.')
        if cert_cname is None:
            raise CLIError(
                'Certificate CNAME must be provided if certificate is provided.')
        try:
            with open(cert_pem, 'r') as pemfile:
                cert_str = pemfile.read()
        except (IOError, OSError) as exc:
            raise CLIError("Error while reading certificate bytes: {}".format(exc))
        try:
            with open(cert_key_pem, 'r') as keyfile:
                key_str = keyfile.read()
        except (IOError, OSError) as exc:
            raise CLIError("Error while reading certificate key bytes: {}".format(exc))
        ssl_enabled = 'Enabled'

    # confirm user logged in
    az_login(yes=yes)

    # prompt user to confirm subscription
    az_check_subscription(yes=yes, context=context)

    # try to register before creating any resources
    try:
        az_register_provider('Microsoft.MachineLearningCompute')
    except CloudError:
        raise CLIError('Your subscription is not whitelisted for provisioning Machine '
                       'Learning environments. Please contact deployml@microsoft.com '
                       'with your subscription info to get whitelisted.')

    # if use passed storage acct ID, verify that it exists
    if storage_arm_id is not None:
        client = client_factory.get_mgmt_service_client(
            ResourceManagementClient).resources
        try:
            # raises CloudError if resource does not exist
            client.get_by_id(storage_arm_id, api_version='2017-06-01')
            active_sub_id = az_get_active_subscription_id().lower()
            storage_subscription = storage_arm_id.split('/')[2].lower()
            if active_sub_id != storage_subscription:
                raise CLIError('Storage account must be in the same subscription as the '
                               'compute. Target subscription: {}, storage subscription: '
                               '{}'.format(active_sub_id, storage_subscription))
        except IndexError:
            # this shouldn't happen, as the check_existence call should throw CloudError
            raise CLIError('Malformed storage ID: {}'.format(storage_arm_id))
        except CloudError as exc:
            raise CLIError('Error validating storage with ID {}: {}'.format(storage_arm_id,
                                                                            exc))

    # redirect east us 2 euap to east us 2
    resource_group_location = location
    if 'euap' in location.lower():
        resource_group_location = location.lower().replace('euap', '')

    # verify/create RG
    if resource_group is None:
        resource_group = az_create_resource_group(context, cluster_name,
                                                  location=resource_group_location)
    else:
        az_create_resource_group(context, resource_group, append='', location=resource_group_location)

    # TODO - REMOVE THIS once MLCRP does this provisioning for 1p
    from ._acs_util import create_or_validate_sp
    service_principal, client_secret = create_or_validate_sp(service_principal,
                                                             client_secret,
                                                             cluster_name)

    print('Provisioning compute resources...')
    # call MLCRP
    resp = create_compute_resource(resource_group, cluster_name, service_principal,
                                   client_secret, location, agent_count, cert_str,
                                   key_str, ssl_enabled, storage_arm_id, cert_cname,
                                   master_count)

    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        raise CLIError('Received bad response from MLC RP: {}\n{}\n{}'.format(resp.status_code,
                                                                              resp.headers,
                                                                              resp.content))

    print('Resource creation submitted successfully.')
    print('Resources may take 10-20 minutes to be completely provisioned.')
    print('To see if your environment is ready to use, run:')
    print('  az ml env show -g {} -n {}'.format(resource_group, cluster_name))
    print('Once your environment has successfully provisioned, you can set it as your target context using:')
    print('  az ml env set -g {} -n {}'.format(resource_group, cluster_name))
    return SUCCESS_RETURN_CODE


def compute_delete(resource_group, cluster_name, context=cli_context):
    """
    Delete an MLCRP-provisioned resource.
    :param resource_group:
    :param cluster_name:
    :param context:
    :return:
    """
    _compute_delete(resource_group, cluster_name, context)


def _compute_delete(resource_group, cluster_name, context=cli_context):
    resp = delete_compute_resource(resource_group, cluster_name)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        raise CLIError('Received bad response from MLC RP: {}\n{}\n{}'.format(resp.status_code,
                                                                              resp.headers,
                                                                              resp.content))
    print('Resource deletion successfully submitted.')
    print('Resources may take 1-2 minutes to be completely deprovisioned.')
    return SUCCESS_RETURN_CODE


def compute_set(resource_group, cluster_name, context=cli_context):
    """
    Set the active MLC environment.
    :param resource_group:
    :param cluster_name:
    :param context:
    :return:
    """
    _compute_set(resource_group, cluster_name, context)


def _compute_set(resource_group, cluster_name, context):
    compute_resource = get_compute_resource(resource_group, cluster_name)
    state = compute_resource.provisioning_state.strip()
    if state.lower() != OperationStatus.succeeded.name.lower():
        raise CLIError('Resource with group {} and name {} cannot be set, '
                       'as its provisioning state is {}. Provisioning state {} '
                       'is required.'.format(
            resource_group, cluster_name, state, OperationStatus.succeeded.name))
    context.set_compute(resource_group, cluster_name)
    return SUCCESS_RETURN_CODE


def compute_show(resource_group=None, cluster_name=None, verb=False, context=cli_context):
    """
    Show an MLC resource; If resource_group or cluster_name are not provided, shows the
    active MLC env.
    :param resource_group:
    :param cluster_name:
    :param verb:
    :param context:
    :return:
    """
    if context.in_local_mode():
        from .env import env_describe
        env_describe(context)
        return None, verb
    _, result = _compute_show(resource_group, cluster_name, context)
    return result, verb


def _compute_show(resource_group, cluster_name, context):
    if resource_group is None or cluster_name is None:
        print('Current env:')
        return SUCCESS_RETURN_CODE, get_current_compute_resource(context)

    return SUCCESS_RETURN_CODE, get_compute_resource(resource_group, cluster_name)


def get_credentials(resource_group, cluster_name, install_kube_config, verb, context=cli_context):
    """
    List the keys for an environment.
    :param resource_group:
    :param cluster_name:
    :param install_kube_config:
    :param verb:
    :param context:
    :return:
    """
    return _get_credentials(resource_group, cluster_name, install_kube_config, verb, context)[1]


def _get_credentials(resource_group, cluster_name, install_kube_config, verb, context):
    result = get_compute_resource_keys(resource_group, cluster_name)

    # with nargs='?', when the flag appears but no arg appears, the value is None
    # when the flag does not appear, the value is '' (default)
    if install_kube_config is None:
        context.current_compute_creds = result
        context.update_kube_config()
    elif install_kube_config:
        try:
            with open(install_kube_config, 'w') as kube_config:
                kube_config.write(result.container_service.acs_kube_config)
        except (OSError, IOError) as exc:
            raise CLIError(exc)

    return SUCCESS_RETURN_CODE, result
