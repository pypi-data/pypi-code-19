# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import requests
import json
import time
from pkg_resources import resource_string
from azure.cli.core.util import CLIError
from ._constants import MMS_ASYNC_OPERATION_POLLING_INTERVAL_SECONDS
from ._constants import MMS_IMAGE_URL
from ._constants import MMS_OPERATION_URL
from ._constants import MMS_SYNC_TIMEOUT_SECONDS
from ._constants import SUCCESS_RETURN_CODE
from ._host_account_util import get_host_account_token
from ._image_util import image_show_header_to_fn_dict
from ._util import cli_context
from ._util import get_json
from ._util import get_sub_and_account_info
from ._util import get_success_and_resp_str
from ._util import TableResponse
from .manifest import _manifest_create


def image_create(image_type, image_description, manifest_id, driver_file, schema_file, dependencies, runtime,
                 requirements, model_name, model_file, verb, context=cli_context):
    _image_create(image_type, image_description, manifest_id, driver_file, schema_file, dependencies, runtime,
                  requirements, model_name, model_file, verb, context)


def _image_create(image_type, image_description, manifest_id, driver_file, schema_file, dependencies, runtime,
                  requirements, model_name, model_file, verb, context):
    if not manifest_id and not driver_file:
        raise CLIError('Either manifest id or information to create a manifest must be provided')

    base_url, subscription, resource_group, host_account_name = get_sub_and_account_info()
    mms_url = MMS_IMAGE_URL.format(base_url, subscription, resource_group, host_account_name)
    auth_token = get_host_account_token()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(auth_token)}

    json_payload = json.loads(resource_string(__name__, 'data/mmsimagepayloadtemplate.json').decode('ascii'))
    json_payload['description'] = image_description
    json_payload['imageType'] = image_type
    json_payload['registryInfo']['location'] = context.acr_home
    json_payload['registryInfo']['user'] = context.acr_user
    json_payload['registryInfo']['password'] = context.acr_pw

    if manifest_id:
        json_payload['manifestId'] = manifest_id
    else:
        json_payload['manifestId'] = _manifest_create(driver_file, None, schema_file, dependencies, runtime,
                                                      requirements, None, model_name, model_file, verb, context)[1]

    if verb:
        print('Image payload: {}'.format(json_payload))

    try:
        resp = context.http_call('post', mms_url, headers=headers, json=json_payload, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}.'.format(mms_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(mms_url))

    if resp.status_code != 202:
        raise CLIError('Error occurred creating image.\n{}\n{}'.format(resp.headers, resp.content))

    try:
        operation_location = resp.headers['Operation-Location']
    except KeyError:
        raise CLIError('Invalid response header key: Operation-Location')
    create_operation_status_id = operation_location.split('/')[-1]

    operation_url = MMS_OPERATION_URL.format(base_url, subscription, resource_group, host_account_name, create_operation_status_id)
    operation_headers = {'Authorization': 'Bearer {}'.format(auth_token)}

    try:
        operation_resp = context.http_call('get', operation_url, headers=operation_headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}.'.format(operation_url))
    except requests.Timeout:
        raise CLIError('Error, operation request to {} timed out.'.format(operation_url))
    resp_obj = get_json(operation_resp.content, pascal=True)

    while 'State' in resp_obj:
        if operation_resp.status_code == 200:
            try:
                operation_state = resp_obj['State']
            except KeyError:
                raise CLIError('Invalid response key: State')
            print(operation_state)

            if operation_state == 'NotStarted' or operation_state == 'Running':
                time.sleep(MMS_ASYNC_OPERATION_POLLING_INTERVAL_SECONDS)
            elif operation_state == 'Succeeded':
                try:
                    image_id = resp_obj['ResourceLocation'].split('/')[-1]
                except KeyError:
                    raise CLIError('Invalid response key: ResourceLocation')
                print('Image ID: {}'.format(image_id))
                return SUCCESS_RETURN_CODE, image_id
            else:
                raise CLIError('Error creating image: {}'.format(resp_obj))
        else:
            raise CLIError('Error occurred while polling for image_id create operation.\n{}'.format(operation_resp.content))

        try:
            operation_resp = context.http_call('get', operation_url, headers=operation_headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
        except requests.ConnectionError:
            raise CLIError('Error connecting to {}.'.format(operation_url))
        except requests.Timeout:
            raise CLIError('Error, operation request to {} timed out.'.format(operation_url))
        resp_obj = get_json(operation_resp.content, pascal=True)

    raise CLIError('Error, State not found in operation response: {}'.format(resp_obj))


def image_show(image_id, verb, context=cli_context):
    _image_show(image_id, verb, context)


def _image_show(image_id, verb, context):
    base_url, subscription, resource_group, host_account_name = get_sub_and_account_info()
    package_url = MMS_IMAGE_URL.format(base_url, subscription, resource_group, host_account_name) + '/{}'.format(image_id)
    auth_token = get_host_account_token()
    headers = {'Authorization': 'Bearer {}'.format(auth_token)}

    try:
        resp = context.http_call('get', package_url, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}'.format(package_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(package_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp, response_obj=TableResponse(image_show_header_to_fn_dict))[1])
        return SUCCESS_RETURN_CODE
    else:
        raise CLIError('Error occurred while attempting to show image.\n{}'.format(resp.content))


def image_list(verb, context=cli_context):
    _image_list(verb, context)


def _image_list(verb, context):
    base_url, subscription, resource_group, host_account_name = get_sub_and_account_info()
    image_url = MMS_IMAGE_URL.format(base_url, subscription, resource_group, host_account_name)
    auth_token = get_host_account_token()
    headers = {'Authorization': 'Bearer {}'.format(auth_token)}

    try:
        resp = context.http_call('get', image_url, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}'.format(image_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(image_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp, response_obj=TableResponse(image_show_header_to_fn_dict))[1])
        return SUCCESS_RETURN_CODE
    else:
        raise CLIError('Error occurred while attempting to list images.\n{}'.format(resp.content))
