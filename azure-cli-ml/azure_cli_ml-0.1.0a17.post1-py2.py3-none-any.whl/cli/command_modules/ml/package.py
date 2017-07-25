# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import requests
import time
import json
from azure.cli.core.util import CLIError
from azure.ml.api.realtime.swagger_spec_generator import generate_service_swagger
from pkg_resources import resource_string
from ._constants import MMS_SYNC_TIMEOUT_SECONDS
from ._constants import SUCCESS_RETURN_CODE
from ._host_account_util import get_host_account_token
from ._package_util import MMS_PACKAGE_URL
from ._package_util import handle_driver_file
from ._package_util import handle_model_file
from ._package_util import mms_runtime_mapping
from ._package_util import package_show_header_to_fn_dict
from .service._realtimeutilities import upload_dependency
from ._constants import MMS_OPERATION_URL
from ._constants import MMS_ASYNC_OPERATION_POLLING_INTERVAL_SECONDS
from ._util import cli_context
from ._util import get_json
from ._util import get_sub_and_account_info
from ._util import get_success_and_resp_str
from ._util import TableResponse
from ._util import Constants


def package_create(driver_file, model_id, model_name, model_file, model_tags, model_description,
                   package_description, schema_file, dependencies, runtime, requirements,
                   verb, context=cli_context):
    _package_create(driver_file, model_id, model_name, model_file, model_tags, model_description,
                    package_description, schema_file, dependencies, runtime, requirements, verb, context)


def _package_create(driver_file, model_id, model_name, model_file, model_tags, model_description,
                    package_description, schema_file, dependencies, runtime, requirements, verb, context):
    base_url, subscription, resource_group, host_account_name = get_sub_and_account_info()
    mms_url = MMS_PACKAGE_URL.format(base_url, subscription, resource_group, host_account_name)
    auth_token = get_host_account_token()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(auth_token)}

    json_payload = json.loads(resource_string(__name__, 'data/mmspackagepayloadtemplate.json').decode('ascii'))
    json_payload['description'] = package_description
    if runtime in mms_runtime_mapping.keys():
        json_payload['targetRuntime'] = mms_runtime_mapping[runtime]
    else:
        raise CLIError('Provided runtime not supported. Possible runtimes are: {}'.format('|'.join(Constants.supported_runtimes)))
    json_payload['registryInfo']['location'] = context.acr_home
    json_payload['registryInfo']['user'] = context.acr_user
    json_payload['registryInfo']['password']= context.acr_pw

    if not model_file and not model_name and not model_id:
        print("No model information provided, skipping model creation")
        model_info = None
    else:
        model_info = handle_model_file(model_id, model_name, model_file, model_tags, model_description, base_url,
                                       subscription, resource_group, host_account_name, verb, context)

    if model_info:
        json_payload['modelInfo'].append(model_info)

    driver_file_name, driver_file_extension = os.path.splitext(driver_file)
    if driver_file_extension == '.py':
        driver_mime_type = 'application/x-python'
    else:
        raise CLIError('Invalid driver type.')
    driver_package_location = handle_driver_file(driver_file, runtime, verb, context)
    json_payload['assets'].append({'id': 'driver', 'url': driver_package_location, 'mimeType': driver_mime_type})

    schema_arg = None
    if schema_file != '':
        schema_arg = schema_file
        dependencies.append(schema_file)

    # TODO revist this. Currently MMS does not support having swagger as the information that is provided when creating
    # TODO a package does not have a name/version
    # swagger_spec = generate_service_swagger(service_name, schema_arg)
    #
    # temp_dir = tempfile.mkdtemp()
    # swagger_spec_filepath = os.path.join(temp_dir, 'swagger.json')
    # with open(swagger_spec_filepath, 'w') as f:
    #     json.dump(swagger_spec, f)
    # dependencies.append(swagger_spec_filepath)

    if requirements is not '':
        status, location, filename = upload_dependency(context, requirements, verb)
        if status < 0:
            raise CLIError('Error resolving requirements file')
        else:
            json_payload['pipRequirements'] = location

    for dependency in dependencies:
        (status, location, filename) = upload_dependency(context, dependency, verb)
        if status < 0:
            raise CLIError('Error resolving dependency: no such file or directory {}'.format(dependency))
        else:
            # Add the new asset to the payload
            new_asset = {'mimeType': 'application/octet-stream',
                         'id': str(dependency),
                         'url': location,
                         'unpack': status == 1}
            json_payload['assets'].append(new_asset)
            if verb:
                print("Added dependency {} to assets.".format(dependency))

    if verb:
        print('Package payload: {}'.format(json_payload))

    try:
        if verb:
            print('Package post url: {}'.format(mms_url))
        resp = context.http_call('post', mms_url, headers=headers, json=json_payload, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}.'.format(mms_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(mms_url))

    if resp.status_code != 202:
        raise CLIError('Error occurred creating package.\n{}\n{}'.format(resp.headers, resp.content))

    if verb:
        print('Package post response headers: {}\ncontent:{}'.format(resp.headers, resp.content))

    try:
        operation_location = resp.headers['Operation-Location']
    except KeyError:
        raise CLIError('Invalid response header key: Operation-Location')
    create_operation_status_id = operation_location.split('/')[-1]

    operation_url = MMS_OPERATION_URL.format(base_url, subscription, resource_group, host_account_name, create_operation_status_id)
    operation_headers = {'Authorization': 'Bearer {}'.format(auth_token)}

    try:
        if verb:
            print('Calling \'get\' on operation url {}'.format(operation_url))
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
                    package_id = resp_obj['ResourceLocation'].split('/')[-1]
                except KeyError:
                    raise CLIError('Invalid response key: ResourceLocation')
                print('Package ID: {}'.format(package_id))
                return SUCCESS_RETURN_CODE, package_id
            else:
                raise CLIError('Error creating image: {}'.format(resp_obj))
        else:
            raise CLIError('Error occurred while polling for package_id create operation.\n{}'.format(operation_resp.content))

        try:
            operation_resp = context.http_call('get', operation_url, headers=operation_headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
        except requests.ConnectionError:
            raise CLIError('Error connecting to {}.'.format(operation_url))
        except requests.Timeout:
            raise CLIError('Error, operation request to {} timed out.'.format(operation_url))
        resp_obj = get_json(operation_resp.content, pascal=True)

    raise CLIError('Error, State not found in operation response: {}\nHeaders: {}'.format(resp_obj, operation_resp.headers))


def package_show(package_id, verb, context=cli_context):
    _package_show(package_id, verb, context)


def _package_show(package_id, verb, context):
    base_url, subscription, resource_group, host_account_name = get_sub_and_account_info()
    package_url = MMS_PACKAGE_URL.format(base_url, subscription, resource_group, host_account_name) + '/{}'.format(package_id)
    auth_token = get_host_account_token()
    headers = {'Authorization': 'Bearer {}'.format(auth_token)}

    try:
        resp = context.http_call('get', package_url, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}'.format(package_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(package_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp, response_obj=TableResponse(package_show_header_to_fn_dict))[1])
        return SUCCESS_RETURN_CODE
    else:
        raise CLIError('Error occurred while attempting to show package.\n{}'.format(resp.content))


def package_list(verb, context=cli_context):
    _package_list(verb, context)


def _package_list(verb, context):
    base_url, subscription, resource_group, host_account_name = get_sub_and_account_info()
    package_url = MMS_PACKAGE_URL.format(base_url, subscription, resource_group, host_account_name)
    auth_token = get_host_account_token()
    headers = {'Authorization': 'Bearer {}'.format(auth_token)}

    try:
        resp = context.http_call('get', package_url, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}'.format(package_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(package_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp, response_obj=TableResponse(package_show_header_to_fn_dict))[1])
        return SUCCESS_RETURN_CODE
    else:
        raise CLIError('Error occurred while attempting to list packages.\n{}'.format(resp.content))
