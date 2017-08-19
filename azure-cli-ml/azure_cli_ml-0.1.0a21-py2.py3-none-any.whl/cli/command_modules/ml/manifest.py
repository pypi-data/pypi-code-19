# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import requests
import json
from azure.cli.core.util import CLIError
from pkg_resources import resource_string
from .service._realtimeutilities import upload_dependency
from ._constants import MMS_API_VERSION
from ._constants import MMS_MANIFEST_URL_ENDPOINT
from ._constants import MMS_SYNC_TIMEOUT_SECONDS
from ._constants import SUCCESS_RETURN_CODE
from ._manifest_util import manifest_show_header_to_fn_dict
from ._manifest_util import mms_runtime_mapping
from ._manifest_util import handle_driver_file
from ._manifest_util import handle_model_file
from ._util import cli_context
from ._util import get_auth_header
from ._util import get_json
from ._util import get_current_model_management_url_base
from ._util import get_success_and_resp_str
from ._util import TableResponse
from ._util import PaginatedTableResponse
from ._util import add_sdk_to_requirements
from ._util import wrap_driver_file
from ._constants import SUPPORTED_RUNTIMES


def manifest_create(manifest_name, driver_file, manifest_description, schema_file, dependencies, runtime, requirements,
                    model_ids, model_file, verb, context=cli_context):
    _manifest_create(manifest_name, driver_file, manifest_description, schema_file, dependencies, runtime, requirements,
                     model_ids, model_file, verb, context)


def _manifest_create(manifest_name, driver_file, manifest_description, schema_file, dependencies, runtime, requirements,
                     model_ids, model_file, verb, context):
    mms_url = get_current_model_management_url_base() + MMS_MANIFEST_URL_ENDPOINT
    auth_header = get_auth_header()
    headers = {'Content-Type': 'application/json', 'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}

    json_payload = json.loads(resource_string(__name__, 'data/mmsmanifestpayloadtemplate.json').decode('ascii'))
    json_payload['name'] = manifest_name
    json_payload['description'] = manifest_description
    if not runtime:
        raise CLIError('Missing runtime. Possible runtimes are: {}'.format('|'.join(SUPPORTED_RUNTIMES)))
    elif runtime in mms_runtime_mapping.keys():
        json_payload['targetRuntime']['runtimeType'] = mms_runtime_mapping[runtime]
    else:
        raise CLIError('Provided runtime not supported. Possible runtimes are: {}'.format('|'.join(SUPPORTED_RUNTIMES)))

    # add SDK to requirements file
    requirements = add_sdk_to_requirements(requirements)

    status, location, filename = upload_dependency(context, requirements, verb)
    if status < 0:
        raise CLIError('Error resolving requirements file')
    else:
        json_payload['targetRuntime']['properties']['pipRequirements'] = location

    if not model_file and not model_ids:
        print("No model information provided, skipping model creation")
        model_info = None
    else:
        model_info = handle_model_file(model_ids, model_file, verb, context)

    if model_info:
        json_payload['modelIds'] = model_info

    driver_file_name, driver_file_extension = os.path.splitext(driver_file)
    if driver_file_extension == '.py':
        driver_mime_type = 'application/x-python'

        # wrap user driver
        wrapped_driver_file = wrap_driver_file(driver_file, schema_file, dependencies)
    else:
        raise CLIError('Invalid driver type.')
    driver_package_location = handle_driver_file(wrapped_driver_file, verb, context)
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
                         'id': filename[:32],
                         'url': location,
                         'unpack': status == 1}
            json_payload['assets'].append(new_asset)
            if verb:
                print("Added dependency {} to assets.".format(dependency))

    if verb:
        print('Manifest payload: {}'.format(json_payload))

    try:
        resp = context.http_call('post', mms_url, params=params, headers=headers, json=json_payload, timeout=MMS_SYNC_TIMEOUT_SECONDS)
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
    manifest_url = get_current_model_management_url_base() + MMS_MANIFEST_URL_ENDPOINT + '/{}'.format(manifest_id)
    auth_header = get_auth_header()
    headers = {'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}

    try:
        resp = context.http_call('get', manifest_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}'.format(manifest_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(manifest_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp, response_obj=PaginatedTableResponse('Value', manifest_show_header_to_fn_dict))[1])
        return SUCCESS_RETURN_CODE
    else:
        raise CLIError('Error occurred while attempting to show manifest.\n{}'.format(resp.content))


def manifest_list(verb, context=cli_context):
    _manifest_list(verb, context)


def _manifest_list(verb, context):
    manifest_url = get_current_model_management_url_base() + MMS_MANIFEST_URL_ENDPOINT
    auth_header = get_auth_header()
    headers = {'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}

    try:
        resp = context.http_call('get', manifest_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}'.format(manifest_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(manifest_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp, response_obj=PaginatedTableResponse('Value', manifest_show_header_to_fn_dict))[1])
        return SUCCESS_RETURN_CODE
    else:
        raise CLIError('Error occurred while attempting to list manifests.\n{}'.format(resp.content))
