# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import requests
import uuid
from collections import OrderedDict
from datetime import datetime
from datetime import timedelta
from azure.cli.core.util import CLIError
from azure.storage.blob import BlobPermissions
from azure.storage.blob import BlockBlobService
from azure.storage.blob import ContentSettings
from pkg_resources import resource_string
from .model import _model_register
from ._constants import MMS_SYNC_TIMEOUT_SECONDS
from ._model_util import MMS_MODEL_URL
from ._util import get_json
from ._util import TraversalFunction


manifest_show_header_to_fn_dict = OrderedDict([('Id', TraversalFunction(('Id',))),
                                               ('Description', TraversalFunction(('Description',))),
                                               ('Target_Runtime', TraversalFunction(('TargetRuntime',))),
                                               ('Model_Ids', TraversalFunction(('ModelIds',)))])

mms_runtime_mapping = {'spark-py': 'SparkPython', 'cntk-py': 'CNTKPython', 'scikit-py': 'ScikitPython', 'tlc': 'Tlc37'}


def handle_model_file(model_id, model_name, model_file, base_url, subscription,
                      resource_group, hosting_account, verb, context):
    if model_id:
        model_info = model_id
    elif model_file:
        if not model_name:
            model_name = os.path.basename(model_file)
        model_create_status, model_info = _model_register(model_file, model_name, None, None, verb, context)
    elif model_name:
        mms_url = MMS_MODEL_URL.format(base_url, subscription, resource_group, hosting_account)
        mms_url += '?name={}'.format(model_name)

        try:
            resp = context.http_call('get', mms_url, timeout=MMS_SYNC_TIMEOUT_SECONDS)
        except requests.ConnectionError:
            raise CLIError('Error connecting to {}.'.format(mms_url))
        except requests.Timeout:
            raise CLIError('Error, request to {} timed out.'.format(mms_url))

        if resp.status_code == 200:
            models = get_json(resp.content, pascal=True)
            try:
                current_latest_version = -1
                model_info = None
                for model in models:
                    model_version = model['Version']
                    if model_version > current_latest_version:
                        current_latest_version = model_version
                        model_info = model['Id']
                if not model_info:
                    raise CLIError('No models found with name "{}"'.format(model_name))
            except KeyError:
                raise CLIError('Invalid model key: Id')
        else:
            raise CLIError('Error occurred attempting to get model with name {}\n{}'.format(model_name, resp.content))
    else:
        return None

    return model_info


def handle_driver_file(driver_file, verb, context):
    if os.path.isfile(driver_file):
        with open(driver_file, 'r') as scorefile:
            code = scorefile.read()
    else:
        raise CLIError("Error: No such file {}".format(driver_file))

    az_container_name = 'amlbdpackages'
    az_blob_name = str(uuid.uuid4()) + '.py'
    bbs = BlockBlobService(account_name=context.az_account_name,
                           account_key=context.az_account_key)
    bbs.create_container(az_container_name)
    bbs.create_blob_from_text(az_container_name, az_blob_name, code,
                              content_settings=ContentSettings(content_type='application/text'))
    blob_sas = bbs.generate_blob_shared_access_signature(
        az_container_name,
        az_blob_name,
        BlobPermissions.READ,
        datetime.utcnow() + timedelta(days=30))
    upload_location = 'http://{}.blob.core.windows.net/{}/{}?{}'.format(context.az_account_name,
                                                                        az_container_name, az_blob_name, blob_sas)

    if verb:
        print("Driver uploaded to " + upload_location)

    return upload_location
