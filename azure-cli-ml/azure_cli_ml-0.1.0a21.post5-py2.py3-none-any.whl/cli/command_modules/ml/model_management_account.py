# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import os
import sys
from azure.cli.core.util import CLIError
from ._constants import MMS_MODEL_MANAGEMENT_ACCOUNT_PROFILE
from ._constants import SUCCESS_RETURN_CODE
from ._modelmanagementaccountssdk.models.azure_machine_learning_model_management_account_enums import SkuName
from ._modelmanagementaccountssdk.models.error_response import ErrorResponseException
from ._modelmanagementaccountssdk.models.model_management_account import ModelManagementAccount
from ._modelmanagementaccountssdk.models.model_management_account_update_properties import ModelManagementAccountUpdateProperties
from ._modelmanagementaccountssdk.models.sku import Sku
from ._model_management_account_util import get_service_client
from ._model_management_account_util import get_config_dir
from ._model_management_account_util import get_current_model_management_account
from ._model_management_account_util import handle_error_response_exception
from ._model_management_account_util import serialize_model_management_account
from ._az_util import az_register_provider
from msrestazure.azure_exceptions import CloudError


def model_management_account_create(resource_group, name, location, sku_name, sku_instances, tags,
                                    description, verb):
    """
    Create a Model Management Account
    :param resource_group: 
    :param name: 
    :param location: 
    :param sku_name:
    :param sku_instances: 
    :param tags: 
    :param description: 
    :param verb: 
    :return: 
    """
    _model_management_account_create(resource_group, name, location, sku_name, sku_instances, tags,
                                     description, verb)


def _model_management_account_create(resource_group, model_management_account_name, location, sku_name,
                                     sku_instances, tags, description, verb):
    try:
        az_register_provider('Microsoft.MachineLearningModelManagement')
    except CloudError:
        raise CLIError('Your subscription is not whitelisted for provisioning Model '
                       'Management accounts. Please contact deployml@microsoft.com '
                       'with your subscription info to get whitelisted.')

    model_management_account_client = get_service_client()
    sku_name = sku_name.capitalize()
    possible_sku_names = [name.value for name in SkuName]
    if sku_name not in possible_sku_names:
        raise CLIError('Invalid sku name provided. Possible values are {}'.format('|'.join(possible_sku_names)))
    elif sku_instances < 1 or sku_instances > 16:
        raise CLIError('Invalid sku instances provided. Must be a value between 1 and 16 inclusive')
    sku = Sku(sku_name, sku_instances)

    if tags:
        try:
            print(tags)
            tags = json.loads(tags)
            if not isinstance(tags, dict):
                raise ValueError
        except ValueError:
            if sys.platform == 'win32':
                tag_format = '\'{\\"key\\": \\"value\\"}\''
            else:
                tag_format = '\'{"key": "value"}\''
            raise CLIError('Invalid format provided for tags. Please provide tags in the format {}'.format(tag_format))
    model_management_account = ModelManagementAccount(location, tags, sku, description)

    try:
        model_management_account_client.create_or_update(resource_group, model_management_account_name, model_management_account)
        return _model_management_account_set(resource_group, model_management_account_name, verb)
    except ErrorResponseException as e:
        error_code, error_message = handle_error_response_exception(e)
        raise CLIError('{}, {}'.format(error_code, error_message))



def model_management_account_show(resource_group, name, verb):
    """
    Show a Model Management Account. If resource_group or name are not provided, shows the active account.
    :param resource_group: 
    :param name: 
    :param verb: 
    :return: 
    """
    _model_management_account_show(resource_group, name, verb)


def _model_management_account_show(resource_group, name, verb):
    if resource_group and name:
        model_management_account_client = get_service_client()
        try:
            model_management_account = model_management_account_client.get(resource_group, name)
            print(json.dumps(serialize_model_management_account(model_management_account_client, model_management_account), indent=2, sort_keys=True))
        except ErrorResponseException as e:
            error_code, error_message = handle_error_response_exception(e)
            raise CLIError('{}, {}'.format(error_code, error_message))
    else:
        model_management_account = get_current_model_management_account()
        print(json.dumps(model_management_account, indent=2, sort_keys=True))

    return SUCCESS_RETURN_CODE


def model_management_account_list(resource_group, verb):
    """
    Gets the Model Management Accounts in the current subscriptiong. Filters by resource_group if provided.
    :param resource_group: 
    :param verb: 
    :return: 
    """
    _model_management_account_list(resource_group, verb)


def _model_management_account_list(resource_group, verb):
    model_management_account_client = get_service_client()
    try:
        if resource_group:
            result = model_management_account_client.list_by_resource_group(resource_group)
        else:
            result = model_management_account_client.list_by_subscription_id()

        for model_management_account in result:
            print(json.dumps(serialize_model_management_account(model_management_account_client, model_management_account), indent=2, sort_keys=True))
        return SUCCESS_RETURN_CODE
    except ErrorResponseException as e:
        error_code, error_message = handle_error_response_exception(e)
        raise CLIError('{}, {}'.format(error_code, error_message))


def model_management_account_update(resource_group, name, sku_name, sku_instances, tags, description, verb):
    """
    Update an existing Model Management Account
    :param resource_group: 
    :param name: 
    :param sku_name:
    :param sku_instances: 
    :param tags: 
    :param description: 
    :param verb: 
    :return: 
    """
    _model_management_account_update(resource_group, name, sku_name, sku_instances, tags, description, verb)


def _model_management_account_update(resource_group, name, sku_name, sku_instances, tags, description, verb):
    model_management_account_client = get_service_client()

    if sku_name and sku_instances:
        sku_name = sku_name.capitalize()
        possible_sku_names = [name.value for name in SkuName]
        if sku_name not in possible_sku_names:
            raise CLIError('Invalid sku name provided. Possible values are {}'.format('|'.join(possible_sku_names)))
        elif sku_instances < 1 or sku_instances > 16:
            raise CLIError('Invalid sku instances provided. Must be a value between 1 and 16 inclusive')

        sku = Sku(sku_name, sku_instances)
    elif not sku_name and not sku_instances:
        sku = None
    else:
        if not sku_name:
            raise CLIError('Error, please provide sku name')
        else:
            raise CLIError('Error, please provide sku instances')

    if tags:
        try:
            print(tags)
            tags = json.loads(tags)
            if not isinstance(tags, dict):
                raise ValueError
        except ValueError:
            if sys.platform == 'win32':
                tag_format = '\'{\\"key\\": \\"value\\"}\''
            else:
                tag_format = '\'{"key": "value"}\''
            raise CLIError('Invalid format provided for tags. Please provide tags in the format {}'.format(tag_format))

    model_management_account_update_properties = ModelManagementAccountUpdateProperties(tags, sku, description)

    try:
        model_management_account = model_management_account_client.update(resource_group, name, model_management_account_update_properties)
        print(json.dumps(serialize_model_management_account(model_management_account_client, model_management_account), indent=2, sort_keys=True))
        return SUCCESS_RETURN_CODE
    except ErrorResponseException as e:
        error_code, error_message = handle_error_response_exception(e)
        raise CLIError('{}, {}'.format(error_code, error_message))


def model_management_account_delete(resource_group, name, verb):
    """
    Delete a specified Model Management Account
    :param resource_group: 
    :param name: 
    :param verb: 
    :return: 
    """
    _model_management_account_delete(resource_group, name, verb)


def _model_management_account_delete(resource_group, name, verb):
    model_management_account_client = get_service_client()
    try:
        model_management_account_client.delete(resource_group, name)
        return SUCCESS_RETURN_CODE
    except ErrorResponseException as e:
        error_code, error_message = handle_error_response_exception(e)
        raise CLIError('{}, {}'.format(error_code, error_message))


def model_management_account_set(resource_group, name, verb):
    """
    Set the active Model Management Account
    :param resource_group: 
    :param name: 
    :param verb: 
    :return: 
    """
    _model_management_account_set(resource_group, name, verb)


def _model_management_account_set(resource_group, name, verb):
    model_management_account_client = get_service_client()
    azure_folder = get_config_dir()
    model_management_account_file = os.path.join(azure_folder, MMS_MODEL_MANAGEMENT_ACCOUNT_PROFILE)

    try:
        model_management_account = model_management_account_client.get(resource_group, name)
        serialized_model_management_account = serialize_model_management_account(model_management_account_client, model_management_account)
        print(json.dumps(serialized_model_management_account, indent=2, sort_keys=True))
        with open(model_management_account_file, 'w') as ha_file:
            json.dump(serialized_model_management_account, ha_file)
        return SUCCESS_RETURN_CODE
    except ErrorResponseException as e:
        error_code, error_message = handle_error_response_exception(e)
        raise CLIError('{}, {}'.format(error_code, error_message))
