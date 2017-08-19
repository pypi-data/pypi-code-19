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
from ._az_util import az_create_app_insights_account
from ._az_util import az_get_app_insights_account
from ._compute_util import create_compute_resource
from ._compute_util import delete_compute_resource
from ._compute_util import get_compute_resource
from ._compute_util import get_current_compute_resource
from azure.cli.core.util import CLIError
from ._constants import MLC_CLIENT_ENUMS_PATH
from importlib import import_module
mlc_client_enums = import_module(MLC_CLIENT_ENUMS_PATH, package=__package__)
OperationStatus = mlc_client_enums.OperationStatus

import azure.cli.core.azlogging as azlogging
logger = azlogging.get_az_logger(__name__)


def compute_create(cluster_name, service_principal_app_id, service_principal_password,
                   location, resource_group=None, agent_count=2, context=cli_context):
    _compute_create(resource_group, cluster_name, service_principal_app_id,
                    service_principal_password, location, agent_count, context)


def _compute_create(resource_group, cluster_name, service_principal, client_secret,
                    location, agent_count=2, context=cli_context):
    if location is None:
        raise CLIError('Location must be specified for cluster creation.')

    # short term--keeps users from hitting location issue until better error parsing
    supported_locations = ['eastus2']
    if location not in supported_locations:
        raise CLIError('Location {} not supported. Supported location: {}'.format(
            location, ','.join(supported_locations)))

    # confirm user logged in
    az_login()

    # prompt user to confirm subscription
    az_check_subscription()

    # verify/create RG
    if resource_group is None:
        resource_group = az_create_resource_group(context, cluster_name)
    else:
        az_create_resource_group(context, resource_group, append='')

    # TODO - REMOVE THIS once MLCRP does this provisioning for 1p
    from ._acs_util import create_or_validate_sp
    service_principal, client_secret = create_or_validate_sp(service_principal,
                                                             client_secret,
                                                             cluster_name)
    # TODO - REMOVE once MLCRP creates AppInsights
    print('Creating app insights account...')
    deployment = az_create_app_insights_account(cluster_name,
                                                resource_group,
                                                no_wait=False).result()

    app_insights_account_name, app_insights_account_key = az_get_app_insights_account(
        deployment)

    print('Provisioning compute resources...')
    # call MLCRP
    resp = create_compute_resource(resource_group, cluster_name, service_principal,
                                   client_secret, app_insights_account_name,
                                   app_insights_account_key, location, agent_count)

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
