# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import requests
import json
from azure.cli.core.util import CLIError
from azure.ml.api.realtime.swagger_spec_generator import generate_service_swagger
from pkg_resources import resource_string
from .service._realtimeutilities import upload_dependency
from ._constants import MMS_MANIFEST_URL
from ._constants import MMS_SYNC_TIMEOUT_SECONDS
from ._constants import SUCCESS_RETURN_CODE
from ._host_account_util import get_host_account_token
from ._manifest_util import manifest_show_header_to_fn_dict
from ._manifest_util import mms_runtime_mapping
from ._manifest_util import handle_driver_file
from ._manifest_util import handle_model_file
from ._util import cli_context
from ._util import get_json
from ._util import get_sub_and_account_info
from ._util import get_success_and_resp_str
from ._util import TableResponse
from ._constants import SUPPORTED_RUNTIMES


def manifest_create(driver_file, manifest_description, schema_file, dependencies, runtime, requirements, model_id,
                    model_name, model_file, verb, context=cli_context):
    _manifest_create(driver_file, manifest_description, schema_file, dependencies, runtime, requirements, model_id,
                     model_name, model_file, verb, context)


def _manifest_create(driver_file, manifest_description, schema_file, dependencies, runtime, requirements, model_id,
                     model_name, model_file, verb, context):
    base_url, subscription, resource_group, host_account_name = get_sub_and_account_info()
    mms_url = MMS_MANIFEST_URL.format(base_url, subscription, resource_group, host_account_name)
    auth_token = get_host_account_token()
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer {}'.format(auth_token)}

    json_payload = json.loads(resource_string(__name__, 'data/mmsmanifestpayloadtemplate.json').decode('ascii'))
    json_payload['description'] = manifest_description
    if runtime in mms_runtime_mapping.keys():
        json_payload['targetRuntime']['runtimeType'] = mms_runtime_mapping[runtime]
    else:
        raise CLIError('Provided runtime not supported. Possible runtimes are: {}'.format('|'.join(SUPPORTED_RUNTIMES)))

    if requirements is not '':
        status, location, filename = upload_dependency(context, requirements, verb)
        if status < 0:
            raise CLIError('Error resolving requirements file')
        else:
            json_payload['targetRuntime']['properties']['pipRequirements'] = location

    if not model_file and not model_name and not model_id:
        print("No model information provided, skipping model creation")
        model_info = None
    else:
        model_info = handle_model_file(model_id, model_name, model_file, base_url, subscription, resource_group,
                                       host_account_name, verb, context)

    if model_info:
        json_payload['modelIds'].append(model_info)

    driver_file_name, driver_file_extension = os.path.splitext(driver_file)
    if driver_file_extension == '.py':
        driver_mime_type = 'application/x-python'
    else:
        raise CLIError('Invalid driver type.')
    driver_package_location = handle_driver_file(driver_file, verb, context)
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
        resp = context.http_call('post', mms_url, headers=headers, json=json_payload, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}.'.format(mms_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(mms_url))

    if resp.status_code == 200:
        print('Successfully created manifest')
        print(get_success_and_resp_str(context, resp, response_obj=TableResponse(manifest_show_header_to_fn_dict))[1])
        manifest = get_json(resp.content, pascal=True)
        try:
            return SUCCESS_RETURN_CODE, manifest['Id']
        except KeyError:
            raise CLIError('Invalid manifest key: Id')
    else:
        raise CLIError('Error occurred creating manifest.\n{}'.format(resp.content))


def manifest_show(manifest_id, verb, context=cli_context):
    _manifest_show(manifest_id, verb, context)


def _manifest_show(manifest_id, verb, context):
    base_url, subscription, resource_group, host_account_name = get_sub_and_account_info()
    package_url = MMS_MANIFEST_URL.format(base_url, subscription, resource_group, host_account_name) + '/{}'.format(manifest_id)
    auth_token = get_host_account_token()
    headers = {'Authorization': 'Bearer {}'.format(auth_token)}

    try:
        resp = context.http_call('get', package_url, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}'.format(package_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(package_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp, response_obj=TableResponse(manifest_show_header_to_fn_dict))[1])
        return SUCCESS_RETURN_CODE
    else:
        raise CLIError('Error occurred while attempting to show manifest.\n{}'.format(resp.content))


def manifest_list(verb, context=cli_context):
    _manifest_list(verb, context)


def _manifest_list(verb, context):
    base_url, subscription, resource_group, host_account_name = get_sub_and_account_info()
    manifest_url = MMS_MANIFEST_URL.format(base_url, subscription, resource_group, host_account_name)
    auth_token = get_host_account_token()
    headers = {'Authorization': 'Bearer {}'.format(auth_token)}

    try:
        resp = context.http_call('get', manifest_url, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}'.format(manifest_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(manifest_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp, response_obj=TableResponse(manifest_show_header_to_fn_dict))[1])
        return SUCCESS_RETURN_CODE
    else:
        raise CLIError('Error occurred while attempting to list manifests.\n{}'.format(resp.content))
