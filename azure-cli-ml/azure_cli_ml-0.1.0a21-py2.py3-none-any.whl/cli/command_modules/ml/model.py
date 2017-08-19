# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import requests
import json
from azure.cli.core.util import CLIError
from pkg_resources import resource_string
from uuid import UUID
from .service._realtimeutilities import upload_dependency
from ._constants import MMS_API_VERSION
from ._constants import MMS_MODEL_URL_ENDPOINT
from ._constants import MMS_SYNC_TIMEOUT_SECONDS
from ._constants import SUCCESS_RETURN_CODE
from ._model_util import model_show_header_to_fn_dict
from ._util import cli_context
from ._util import get_auth_header
from ._util import get_json
from ._util import get_current_model_management_url_base
from ._util import get_success_and_resp_str
from ._util import TableResponse
from ._util import PaginatedTableResponse


def model_register(model_path, model_name, tags, description, verb, context=cli_context):
    _model_register(model_path, model_name, tags, description, verb, context)


def _model_register(model_path, model_name, tags, description, verb, context):
    unpack, model_url, filename = upload_dependency(context, model_path, verb)
    if unpack < 0:
        raise CLIError('Error resolving model: no such file or directory {}'.format(model_path))
    auth_token = get_auth_header()
    headers = {'Content-Type': 'application/json', 'Authorization': auth_token}
    params = {'api-version': MMS_API_VERSION}

    json_payload = json.loads(resource_string(__name__, 'data/mmsmodelpayloadtemplate.json').decode('ascii'))
    json_payload['name'] = model_name
    json_payload['url'] = model_url
    json_payload['unpack'] = unpack == 1
    if tags:
        json_payload['tags'] = tags
    if description:
        json_payload['description'] = description
    mms_url = get_current_model_management_url_base() + MMS_MODEL_URL_ENDPOINT

    if verb:
        print('Attempting to register model to {}'.format(mms_url))
        print('Attempting to register model with this information: {}'.format(json_payload))

    try:
        if verb:
            print('Model register post url: {}'.format(mms_url))
        resp = context.http_call('post', mms_url, params=params, headers=headers, json=json_payload, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}.'.format(mms_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(mms_url))

    if resp.status_code == 200:
        print('Successfully registered model')
        print(get_success_and_resp_str(context, resp, response_obj=TableResponse(model_show_header_to_fn_dict))[1])
        model = get_json(resp.content, pascal=True)
        try:
            return SUCCESS_RETURN_CODE, model['Id']
        except KeyError:
            raise CLIError('Invalid model key: Id')
    else:
        raise CLIError('Error occurred registering model.\n{}\n{}'.format(resp.headers, resp.content))


def model_show(model, tag, verb, context=cli_context):
    _model_show(model, tag, verb, context)


def _model_show(model, tag, verb, context):
    model_url = get_current_model_management_url_base() + MMS_MODEL_URL_ENDPOINT
    auth_token = get_auth_header()
    headers = {'Authorization': auth_token}
    params = {'api-version': MMS_API_VERSION}

    try:
        # If the model is a valid uuid4, then the ID has been provided
        UUID(model, version=4)
        model_id = model
        model_name = None
        if verb:
            print('Model {} successfully parsed into ID'.format(model))
    except ValueError:
        # If the model is not a valid uuid4, then the name has been provided
        model_name = model
        model_id = None
        if verb:
            print('Model {} parsed into name'.format(model))

    if model_name:
        params['name'] = model_name
    elif model_id:
        model_url += '/{}'.format(model_id)
    else:
        raise CLIError('Error attempting to parse model: {}'.format(model))
    if tag:
        params['tag'] = tag

    try:
        resp = context.http_call('get', model_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}.'.format(model_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(model_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp, response_obj=PaginatedTableResponse('Value', model_show_header_to_fn_dict))[1])
        return SUCCESS_RETURN_CODE
    else:
        raise CLIError('Error occurred showing model.\n{}'.format(resp.content))


def model_list(tag, verb, context=cli_context):
    _model_list(tag, verb, context)


def _model_list(tag, verb, context):
    model_url = get_current_model_management_url_base() + MMS_MODEL_URL_ENDPOINT
    auth_token = get_auth_header()
    params = {'api-version': MMS_API_VERSION}
    
    headers = {'Authorization': auth_token}

    if tag:
        params['tag'] = tag

    try:
        resp = context.http_call('get', model_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}.'.format(model_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(model_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp, response_obj=PaginatedTableResponse('Value', model_show_header_to_fn_dict))[1])
        return SUCCESS_RETURN_CODE
    else:
        raise CLIError('Error occurred listing models.\n{}'.format(resp.content))
