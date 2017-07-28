# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import os
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.util import CLIError
from ._hostingaccountssdk.models.error_response import ErrorResponseException
from ._constants import MMS_HOST_ACCOUNT_PROFILE


def get_service_client():
    from azure.cli.command_modules.ml._hostingaccountssdk import AzureMachineLearningHostingAccount
    return get_mgmt_service_client(AzureMachineLearningHostingAccount).hosting_accounts


def get_config_dir():
    return os.getenv('AZURE_CONFIG_DIR', os.path.expanduser(os.path.join('~', '.azure')))


def get_current_host_account():
    azure_folder = get_config_dir()
    host_account_file = os.path.join(azure_folder, MMS_HOST_ACCOUNT_PROFILE)

    if not os.path.isfile(host_account_file):
        raise CLIError('Host Account not set. Please run \'az ml hostacct set\'')

    with open(host_account_file, 'r') as ha_file:
        host_account = json.load(ha_file)

    return host_account


def get_host_account_token():
    host_account_client = get_service_client()
    host_account = get_current_host_account()
    # Example host account id: /subscriptions/<subscriptionId>/resourceGroups/<resourceGroup>/providers/Microsoft.MachineLearningOperationalization/hostingAccounts/<hostAccountName>
    resource_group = host_account['id'].split('/')[4]
    name = host_account['name']

    try:
        host_account_tokens = host_account_client.list_tokens(resource_group, name)
        access_token = host_account_tokens.access_token
        return access_token
    except ErrorResponseException as e:
        error_code, error_message = handle_error_response_exception(e)
        raise CLIError('{}, {}'.format(error_code, error_message))


def serialize_host_account(host_account_client, host_account):
    """
    Need to manually serialize the pieces of the host account because the client's serializer ignores read-only members
    :param host_account_client: 
    :param host_account: 
    :return: 
    """
    serialized_host_account = {}
    for attr, key_type_map in host_account._attribute_map.items():
        orig_attr = getattr(host_account, attr)
        attr_type = key_type_map['type']
        serialized_host_account[attr] = host_account_client._serialize._serialize(orig_attr, attr_type)
        serialized_host_account['resource_group'] = host_account.id.split('/')[4]

    return serialized_host_account


def handle_error_response_exception(exception):
    """
    Currently the HA SDK can return two different types of exceptions, one from ARM and one from the RP. The ones
    from the RP are deserialized into the ErrorResponse class, which contains a details attribute. This is checked in
    the if statement and used if present. The ARM exception cannot be deserialized into the class, and as such
    error.details is none. In this case, we get the useful information from the exception response itself, in the
    else case.
    :param exception: 
    :return: 
    """
    try:
        if exception.error.details:
            return exception.error.details[0].code, exception.error.details[0].message
        else:
            exception_content = exception.response.json()
            try:
                return exception_content['error']['code'], exception_content['error']['message']
            except KeyError:
                raise CLIError('Invalid exception response key. Exception content: {}'.format(exception_content))
    except AttributeError:
        raise CLIError('Invalid attribute \'error\' in exception. Exception thrown: {}'.format(exception))
