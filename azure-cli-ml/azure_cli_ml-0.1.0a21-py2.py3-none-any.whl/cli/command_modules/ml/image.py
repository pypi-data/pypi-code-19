# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import sys
import requests
import json
import uuid
from pkg_resources import resource_string
from azure.cli.core.util import CLIError
from ._constants import MMS_API_VERSION
from ._constants import MMS_IMAGE_CREATE_OPERATION_POLLING_MAX_TRIES
from ._constants import MMS_IMAGE_URL_ENDPOINT
from ._constants import MMS_OPERATION_URL_ENDPOINT
from ._constants import MMS_SYNC_TIMEOUT_SECONDS
from ._constants import MLC_RESOURCE_ID_FMT
from ._constants import SUCCESS_RETURN_CODE
from ._image_util import image_show_header_to_fn_dict
from ._util import cli_context
from ._util import get_auth_header
from ._util import get_success_and_resp_str
from ._util import get_current_model_management_url_base
from ._util import PaginatedTableResponse
from ._util import poll_mms_async_operation
from ._util import get_json
from .manifest import _manifest_create


def image_create(image_type, image_description, manifest_id, driver_file, schema_file, dependencies, runtime,
                 requirements, model_file, verb, context=cli_context):
    _image_create(image_type, image_description, manifest_id, driver_file, schema_file, dependencies, runtime,
                  requirements, model_file, verb, context)


def _image_create(image_type, image_description, manifest_id, driver_file, schema_file, dependencies, runtime,
                  requirements, model_file, verb, context):
    if not manifest_id and not driver_file:
        raise CLIError('Either manifest id or information to create a manifest must be provided')

    mms_url = get_current_model_management_url_base() + MMS_IMAGE_URL_ENDPOINT
    auth_header = get_auth_header()
    headers = {'Content-Type': 'application/json', 'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}

    if not context.current_compute_name or not context.current_compute_resource_group or not context.current_compute_subscription_id:
        raise CLIError('Missing information for current compute context.\n'
                       'Current Compute Name: {}\nCurrent Compute Resource Group: {}\nCurrent Compute Subscription: {}\n'
                       'Please set your current compute by running:\n'
                       '  az ml env set -n <env_name> -g <env_rg>'.format(context.current_compute_name,
                                                                          context.current_compute_resource_group,
                                                                          context.current_compute_subscription_id))

    json_payload = json.loads(resource_string(__name__, 'data/mmsimagepayloadtemplate.json').decode('ascii'))
    json_payload['description'] = image_description
    json_payload['imageType'] = image_type
    json_payload['computeResourceId'] = MLC_RESOURCE_ID_FMT.format(context.current_compute_subscription_id,
                                                                   context.current_compute_resource_group,
                                                                   context.current_compute_name)

    if manifest_id:
        json_payload['manifestId'] = manifest_id
    else:
        # this is a holdover until images have names
        manifest_name = str(uuid.uuid4()).replace('-', '')[:30]
        json_payload['manifestId'] = _manifest_create(manifest_name, driver_file, None, schema_file, dependencies, runtime,
                                                      requirements, None, model_file, verb, context)[1]

    if verb:
        print('Image payload: {}'.format(json_payload))

    try:
        resp = context.http_call('post', mms_url, params=params, headers=headers, json=json_payload, timeout=MMS_SYNC_TIMEOUT_SECONDS)
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

    if verb:
        print('Operation Id: {}'.format(create_operation_status_id))

    operation_url = get_current_model_management_url_base() + MMS_OPERATION_URL_ENDPOINT.format(create_operation_status_id)
    operation_headers = {'Authorization': auth_header}

    sys.stdout.write('Creating image')
    sys.stdout.flush()
    image_id = poll_mms_async_operation(operation_url, operation_headers, params,
                                        MMS_IMAGE_CREATE_OPERATION_POLLING_MAX_TRIES, context)
    print('Done.')
    print('Image ID: {}'.format(image_id))
    return SUCCESS_RETURN_CODE, image_id


def image_show(image_id, verb, context=cli_context):
    _image_show(image_id, verb, context)


def _image_show(image_id, verb, context):
    image_url = get_current_model_management_url_base() + MMS_IMAGE_URL_ENDPOINT + '/{}'.format(image_id)
    auth_header = get_auth_header()
    headers = {'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}

    try:
        resp = context.http_call('get', image_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}'.format(image_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(image_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp, response_obj=PaginatedTableResponse('Value', image_show_header_to_fn_dict))[1])
        return SUCCESS_RETURN_CODE, get_json(resp.content, pascal=True)
    else:
        raise CLIError('Error occurred while attempting to show image.\n{}'.format(resp.content))


def image_list(verb, context=cli_context):
    _image_list(verb, context)


def _image_list(verb, context):
    image_url = get_current_model_management_url_base() + MMS_IMAGE_URL_ENDPOINT
    auth_header = get_auth_header()
    headers = {'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}

    try:
        resp = context.http_call('get', image_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}'.format(image_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(image_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp, response_obj=PaginatedTableResponse('Value', image_show_header_to_fn_dict))[1])
        return SUCCESS_RETURN_CODE
    else:
        raise CLIError('Error occurred while attempting to list images.\n{}'.format(resp.content))
