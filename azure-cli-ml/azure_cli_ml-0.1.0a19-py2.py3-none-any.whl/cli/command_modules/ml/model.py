# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import requests
import json
from azure.cli.core.util import CLIError
from pkg_resources import resource_string
from uuid import UUID
from .service._realtimeutilities import upload_dependency
from ._constants import MMS_SYNC_TIMEOUT_SECONDS
from ._constants import SUCCESS_RETURN_CODE
from ._model_util import MMS_MODEL_URL
from ._model_util import model_show_header_to_fn_dict
from ._util import cli_context
from ._util import get_auth_token
from ._util import get_json
from ._util import get_sub_and_account_info
from ._util import get_success_and_resp_str
from ._util import TableResponse


def model_register(model_path, model_name, tags, description, verb, context=cli_context):
    _model_register(model_path, model_name, tags, description, verb, context)


def _model_register(model_path, model_name, tags, description, verb, context):
    base_url, subscription, resource_group, host_account_name = get_sub_and_account_info()
    unpack, model_url, filename = upload_dependency(context, model_path, verb)
    if unpack < 0:
        raise CLIError('Error resolving model: no such file or directory {}'.format(model_path))
    auth_token = get_auth_token()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(auth_token)}

    json_payload = json.loads(resource_string(__name__, 'data/mmsmodelpayloadtemplate.json').decode('ascii'))
    json_payload['name'] = model_name
    json_payload['url'] = model_url
    json_payload['unpack'] = unpack == 1
    if tags:
        json_payload['tags'] = tags
    if description:
        json_payload['description'] = description
    mms_url = MMS_MODEL_URL.format(base_url, subscription, resource_group, host_account_name)

    if verb:
        print('Attempting to register model to {}'.format(mms_url))
        print('Attempting to register model with this information: {}'.format(json_payload))

    try:
        if verb:
            print('Model register post url: {}'.format(mms_url))
        resp = context.http_call('post', mms_url, headers=headers, json=json_payload, timeout=MMS_SYNC_TIMEOUT_SECONDS)
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
    base_url, subscription, resource_group, host_account_name = get_sub_and_account_info()
    model_url = MMS_MODEL_URL.format(base_url, subscription, resource_group, host_account_name)
    auth_token = get_auth_token()
    headers = {'Authorization': 'Bearer {}'.format(auth_token)}

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
        model_url += '?name={}'.format(model_name)
        if tag:
            model_url += '&tag={}'.format(tag)
    elif model_id:
        model_url += '/{}'.format(model_id)
        if tag:
            model_url += '?tag={}'.format(tag)
    else:
        raise CLIError('Error attempting to parse model: {}'.format(model))

    try:
        resp = context.http_call('get', model_url, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}.'.format(model_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(model_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp, response_obj=TableResponse(model_show_header_to_fn_dict))[1])
        return SUCCESS_RETURN_CODE
    else:
        raise CLIError('Error occurred showing model.\n{}'.format(resp.content))


def model_list(tag, verb, context=cli_context):
    _model_list(tag, verb, context)


def _model_list(tag, verb, context):
    base_url, subscription, resource_group, host_account_name = get_sub_and_account_info()
    model_url = MMS_MODEL_URL.format(base_url, subscription, resource_group, host_account_name)
    auth_token = get_auth_token()
    
    headers = {'Authorization': 'Bearer {}'.format(auth_token)}

    if tag:
        model_url += '?tag={}'.format(tag)

    try:
        resp = context.http_call('get', model_url, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}.'.format(model_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(model_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp, response_obj=TableResponse(model_show_header_to_fn_dict))[1])
        return SUCCESS_RETURN_CODE
    else:
        raise CLIError('Error occurred listing models.\n{}'.format(resp.content))
