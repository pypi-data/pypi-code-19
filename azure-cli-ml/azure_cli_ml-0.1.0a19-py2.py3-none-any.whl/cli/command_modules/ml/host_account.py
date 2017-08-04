# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import os
from azure.cli.core.util import CLIError
from ._constants import MMS_HOST_ACCOUNT_PROFILE
from ._constants import SUCCESS_RETURN_CODE
from ._constants import POSSIBLE_SKU_NAMES
from ._constants import POSSIBLE_SKU_TIERS
from ._hostingaccountssdk.models.error_response import ErrorResponseException
from ._hostingaccountssdk.models.hosting_account import HostingAccount
from ._hostingaccountssdk.models.hosting_account_update_properties import HostingAccountUpdateProperties
from ._hostingaccountssdk.models.sku import Sku
from ._host_account_util import get_service_client
from ._host_account_util import get_config_dir
from ._host_account_util import get_current_host_account
from ._host_account_util import handle_error_response_exception
from ._host_account_util import serialize_host_account


def host_account_create(resource_group, name, location, sku_name, sku_tier, tags, description, verb):
    _host_account_create(resource_group, name, location, sku_name, sku_tier, tags, description, verb)


def _host_account_create(resource_group, name, location, sku_name, sku_tier, tags, description, verb):
    host_account_client = get_service_client()
    sku_name = sku_name.capitalize()
    sku_tier = sku_tier.capitalize()
    # If this can be done in the Sku constructor instead that would be ideal
    if sku_name not in POSSIBLE_SKU_NAMES:
        raise CLIError('Invalid sku name provided. Possible values are {}'.format(POSSIBLE_SKU_NAMES))
    elif sku_tier not in POSSIBLE_SKU_TIERS:
        raise CLIError('Invalid sku tier provided. Possible values are {}'.format(POSSIBLE_SKU_TIERS))
    sku = Sku(sku_name, sku_tier)

    if tags:
        try:
            tags = json.loads(tags)
        except ValueError as e:
            raise CLIError('Invalid format provided for tags. Please provide tags in the format \'{"key": "value"}\'')
    host_account = HostingAccount(location, tags, sku, description)

    try:
        host_account_client.create_or_update(resource_group, name, host_account)
        return _host_account_set(resource_group, name, verb)
    except ErrorResponseException as e:
        error_code, error_message = handle_error_response_exception(e)
        raise CLIError('{}, {}'.format(error_code, error_message))



def host_account_show(resource_group, name, verb):
    _host_account_show(resource_group, name, verb)


def _host_account_show(resource_group, name, verb):
    if resource_group and name:
        host_account_client = get_service_client()
        try:
            host_account = host_account_client.get(resource_group, name)
            print(json.dumps(serialize_host_account(host_account_client, host_account), indent=2, sort_keys=True))
        except ErrorResponseException as e:
            error_code, error_message = handle_error_response_exception(e)
            raise CLIError('{}, {}'.format(error_code, error_message))
    else:
        host_account = get_current_host_account()
        print(json.dumps(host_account, indent=2, sort_keys=True))

    return SUCCESS_RETURN_CODE


def host_account_list(resource_group, verb):
    _host_account_list(resource_group, verb)


def _host_account_list(resource_group, verb):
    host_account_client = get_service_client()
    try:
        if resource_group:
            result = host_account_client.list_by_resource_group(resource_group)
        else:
            result = host_account_client.list_by_subscription_id()

        for host_account in result:
            print(json.dumps(serialize_host_account(host_account_client, host_account), indent=2, sort_keys=True))
        return SUCCESS_RETURN_CODE
    except ErrorResponseException as e:
        error_code, error_message = handle_error_response_exception(e)
        raise CLIError('{}, {}'.format(error_code, error_message))


def host_account_update(resource_group, name, sku_name, sku_tier, tags, description, verb):
    _host_account_update(resource_group, name, sku_name, sku_tier, tags, description, verb)


def _host_account_update(resource_group, name, sku_name, sku_tier, tags, description, verb):
    host_account_client = get_service_client()

    if sku_name and sku_tier:
        sku_name = sku_name.capitalize()
        sku_tier = sku_tier.capitalize()
        if sku_name not in POSSIBLE_SKU_NAMES:
            raise CLIError('Invalid sku name provided. Possible values are {}'.format(POSSIBLE_SKU_NAMES))
        elif sku_tier not in POSSIBLE_SKU_TIERS:
            raise CLIError('Invalid sku tier provided. Possible values are {}'.format(POSSIBLE_SKU_TIERS))

        sku = Sku(sku_name, sku_tier)
    elif not sku_name and not sku_tier:
        sku = None
    else:
        if not sku_name:
            raise CLIError('Error, please provide sku name')
        else:
            raise CLIError('Error, please provide sku tier')

    if tags:
        tags = json.loads(tags)

    host_account_update_properties = HostingAccountUpdateProperties(tags, sku, description)

    try:
        host_account = host_account_client.update(resource_group, name, host_account_update_properties)
        print(json.dumps(serialize_host_account(host_account_client, host_account), indent=2, sort_keys=True))
        return SUCCESS_RETURN_CODE
    except ErrorResponseException as e:
        error_code, error_message = handle_error_response_exception(e)
        raise CLIError('{}, {}'.format(error_code, error_message))


def host_account_delete(resource_group, name, verb):
    _host_account_delete(resource_group, name, verb)


def _host_account_delete(resource_group, name, verb):
    host_account_client = get_service_client()
    try:
        host_account_client.delete(resource_group, name)
        return SUCCESS_RETURN_CODE
    except ErrorResponseException as e:
        error_code, error_message = handle_error_response_exception(e)
        raise CLIError('{}, {}'.format(error_code, error_message))


def host_account_set(resource_group, name, verb):
    _host_account_set(resource_group, name, verb)


def _host_account_set(resource_group, name, verb):
    host_account_client = get_service_client()
    azure_folder = get_config_dir()
    host_account_file = os.path.join(azure_folder, MMS_HOST_ACCOUNT_PROFILE)

    try:
        host_account = host_account_client.get(resource_group, name)
        serialized_host_account = serialize_host_account(host_account_client, host_account)
        print(json.dumps(serialized_host_account, indent=2, sort_keys=True))
        with open(host_account_file, 'w') as ha_file:
            json.dump(serialized_host_account, ha_file)
        return SUCCESS_RETURN_CODE
    except ErrorResponseException as e:
        error_code, error_message = handle_error_response_exception(e)
        raise CLIError('{}, {}'.format(error_code, error_message))
