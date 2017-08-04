# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long
import argparse

from azure.cli.core.commands import register_cli_argument
from azure.cli.core.commands.parameters import ignore_type
from ._constants import POSSIBLE_SKU_TIERS
from ._constants import POSSIBLE_SKU_NAMES
from ._constants import SUPPORTED_RUNTIMES

# ignore the context--not for users
register_cli_argument('', 'context', arg_type=ignore_type)
register_cli_argument('ml env', 'quiet', arg_type=ignore_type)

# used throughout
register_cli_argument('ml', 'verb', options_list=('-v',), required=False, help='Verbosity flag.', action='store_true')

register_cli_argument('ml service', 'service_name', options_list=('-n',), help='Webservice name.')
register_cli_argument('ml service', 'job_name', options_list=('-j',), help='Job name.')
register_cli_argument('ml service', 'dependencies', options_list=('-d',), action='append',
                      metavar='<dependency> [-d...]', default=[],
                        help='Files and directories required by the service. Multiple dependencies can be specified with additional -d arguments.', required=False)
register_cli_argument('ml service create', 'custom_ice_url', options_list=('-i',), default='', required=False,
                      help=argparse.SUPPRESS)

# batch workflows
register_cli_argument('ml service create batch', 'driver_file', options_list=('-f', '--driver-file'))
register_cli_argument('ml service create batch', 'title', required=False)
register_cli_argument('ml service run batch', 'job_name', required=False, options_list=('-j',), help='Job name. Defaults to a formatted timestamp (%Y-%m-%d_%H%M%S)')
register_cli_argument('ml service run batch', 'wait_for_completion', required=False, options_list=('-w',), action='store_true', help='Flag to wait for job synchronously.')
register_cli_argument('ml service', 'inputs', options_list=('--in',), action='append',
                      metavar='<input_name>[:<default_value>] [--in=...]',
                      help='inputs for service to expect', default=[], required=False)
register_cli_argument('ml service', 'outputs', options_list=('--out',), action='append',
                        metavar='<output_name>[:<default_value>] [--out=...]', default=[],
                        help='outputs for service to expect', required=False)
register_cli_argument('ml service', 'parameters', options_list=('--param',), action='append',
                        metavar='<parameter_name>[:<default_value>] [--param=...]', default=[],
                        help='parameters for service to expect', required=False)

# realtime workflows
register_cli_argument('ml service create realtime', 'app_insights_logging_enabled', options_list=('-l',), action='store_true', default=False, help='Flag to enable App insights logging.', required=False)
register_cli_argument('ml service create realtime', 'model_data_collection_enabled', options_list=('--collect-model-data',), action='store_true', default=False, help='Flag to enable model data collection.', required=False)
register_cli_argument('ml service create realtime', 'num_replicas', options_list=('-z',), type=int, default=1, required=False, help='Number of replicas for a Kubernetes service.')

register_cli_argument('ml service create realtime', 'use_mms', options_list=('--use-mms'), required=False, help=argparse.SUPPRESS, action='store_true')
# Registered Image
register_cli_argument('ml service create realtime', 'image_id', options_list=('--image-id'), required=False, help='Image to deploy to the service.', arg_group='Registered Image')
# Unregistered Image
register_cli_argument('ml service create realtime', 'driver_file', options_list=('-f',), metavar='filename', help='The code file to be deployed.', required=False, arg_group='Unregistered Image')
# TODO: Add documentation about schema file format
register_cli_argument('ml service create realtime', 'schema_file', options_list=('-s',), default='', required=False, help='Input and output schema of the web service.', arg_group='Unregistered Image')
register_cli_argument('ml service create realtime', 'target_runtime', options_list=('-r',), required=False, help='Runtime of the web service. Valid runtimes are {}'.format('|'.join(SUPPORTED_RUNTIMES)), arg_group='Unregistered Image')
register_cli_argument('ml service create realtime', 'dependencies', options_list=('-d',), required=False, action='append', metavar='<dependency> [-d...]', default=[], help='Files and directories required by the service. Multiple dependencies can be specified with additional -d arguments.', arg_group='Unregistered Image')
register_cli_argument('ml service create realtime', 'model_name', options_list=('--model-name'), required=False, help='Model name, if a model, manifest, and image have not be previously registered.', arg_group='Unregistered Image')
register_cli_argument('ml service create realtime', 'model_file', options_list=('--model-file'), default='', help='The model to be deployed.', required=False, arg_group='Unregistered Image')
register_cli_argument('ml service create realtime', 'requirements', options_list=('-p',), metavar='requirements.txt', default='', help='A pip requirements.txt file of packages needed by the code file.', required=False, arg_group='Unregistered Image')
register_cli_argument('ml service create realtime', 'conda_file', options_list=('-c', '--conda-file'), default=None, required=False, help='Path to Conda Environment file.', arg_group='Unregistered Image')
register_cli_argument('ml service create realtime', 'image_type', options_list=('--image-type'), help='The image type to create. Defaults to "Docker".', default='Docker', required=False, arg_group='Unregistered Image')

register_cli_argument('ml service run realtime', 'service_name', options_list=('-n', '--name'), help='Webservice name', required=False)
register_cli_argument('ml service run realtime', 'service_id', options_list=('-i', '--id'), help='The MMS service id to score against', required=False)
register_cli_argument('ml service run realtime', 'input_data', options_list=('-d',), default='', help='The data to use for calling the web service.', required=False)
register_cli_argument('ml service scale realtime', 'num_replicas', options_list=('-z',), type=int, default=1, required=True, help='Number of replicas for a Kubernetes service.')
register_cli_argument('ml service show realtime', 'service_name', options_list=('-n', '--name'), help='Webservice name', required=False)
register_cli_argument('ml service show realtime', 'service_id', options_list=('-i', '--id'), help='The MMS service id to show', required=False)
register_cli_argument('ml service list realtime', 'use_mms', options_list=('--use-mms'), required=False, help=argparse.SUPPRESS, action='store_true')
register_cli_argument('ml service delete realtime', 'service_name', options_list=('-n', '--name'), help='Webservice name', required=False)
register_cli_argument('ml service delete realtime', 'service_id', options_list=('-i', '--id'), help='The MMS service id to delete', required=False)

register_cli_argument('ml service update realtime', 'service_id', options_list=('-i', '--id'), help='The MMS service id to update')
# Registered Image
register_cli_argument('ml service update realtime', 'image_id', options_list=('--image-id'), help='The image id to update the service with', required=False, arg_group='Registered Image')
# Unregistered Image
register_cli_argument('ml service update realtime', 'image_type', options_list=('--image-type'), help='The image type to create. Defaults to "Docker".', default='Docker', required=False, arg_group='Unregistered Image')
register_cli_argument('ml service update realtime', 'driver_file', options_list=('-f',), metavar='filename', help='The code file to be deployed.', required=False, arg_group='Unregistered Image')
register_cli_argument('ml service update realtime', 'model_name', options_list=('--model-name'), required=False, help='Model name, if a model, manifest, and image have not be previously registered.', arg_group='Unregistered Image')
register_cli_argument('ml service update realtime', 'model_file', options_list=('--model-file',), default='', help='The model to be deployed.', required=False, arg_group='Unregistered Image')
register_cli_argument('ml service update realtime', 'schema_file', options_list=('-s',), default='', required=False, help='Input and output schema of the web service.', arg_group='Unregistered Image')
register_cli_argument('ml service update realtime', 'dependencies', options_list=('-d',), required=False, action='append', metavar='<dependency> [-d...]', default=[], help='Files and directories required by the service. Multiple dependencies can be specified with additional -d arguments.', arg_group='Unregistered Image')
register_cli_argument('ml service update realtime', 'target_runtime', options_list=('-r',), required=False, help='Runtime of the web service. Valid runtimes are {}'.format('|'.join(SUPPORTED_RUNTIMES)), arg_group='Unregistered Image')
register_cli_argument('ml service update realtime', 'requirements', options_list=('-p',), metavar='requirements.txt', default='', help='A pip requirements.txt file of packages needed by the code file.', required=False, arg_group='Unregistered Image')

# env workflows
register_cli_argument('ml env setup', 'status', options_list=('-s', '--status'), action='store_true', help='Check the status of an ongoing deployment.', required=False)
register_cli_argument('ml env setup', 'name', options_list=('-n', '--name'), metavar='envName', help='The name of your Azure ML environment (1-20 characters, alphanumeric only).', required=False)
register_cli_argument('ml env setup', 'cluster', options_list=('-c', '--cluster'), action='store_true', help='Sets up an ACS environment.', required=False, default=False)
register_cli_argument('ml env setup', 'service_principal_app_id', options_list=('-a', '--service-principal-app-id'), help='App ID of service principal to use for configuring ACS cluster.', required=False)
register_cli_argument('ml env setup', 'service_principal_password', options_list=('-p', '--service-principal-password'), help='Password associated with service principal.', required=False)

# model workflows
register_cli_argument('ml model register', 'model_path', options_list=('-m', '--model'), help='Model to register.')
register_cli_argument('ml model register', 'model_name', options_list=('-n', '--name'), help='Name of model to register.')
register_cli_argument('ml model register', 'tags', options_list=('-t', '--tag'), action='append', default=[], help='Tags for the model. Multiple tags can be specified with additional -t arguments.', required=False)
register_cli_argument('ml model register', 'description', options_list=('-d', '--description'), help='Description of the model', required=False)
register_cli_argument('ml model show', 'model', options_list=('-m', '--model'), metavar='model', help='Name or ID of model to show')
register_cli_argument('ml model show', 'tag', options_list=('-t', '--tag'), help='If provided, will only show versions of the specified model that have the specified tag', required=False)
register_cli_argument('ml model list', 'tag', options_list=('-t', '--tag'), help='An optional tag to filter the list by', required=False)

# manifest workflows
register_cli_argument('ml manifest create', 'driver_file', options_list=('-f'), help='The code file to be deployed.')
register_cli_argument('ml manifest create', 'runtime', options_list=('-r',), help='Runtime of the web service. Valid runtimes are {}'.format('|'.join(SUPPORTED_RUNTIMES)))
register_cli_argument('ml manifest create', 'manifest_description', options_list=('--manifest-description'), help='Description of the manifest', required=False)
register_cli_argument('ml manifest create', 'schema_file', options_list=('-s', '--schema-file'), default='', help='Schema file to add to the manifest', required=False)
register_cli_argument('ml manifest create', 'dependencies', options_list=('-d', '--dependency'), action='append', default=[], help='Files and directories required by the service. Multiple dependencies can be specified with additional -d arguments.', required=False)
register_cli_argument('ml manifest create', 'requirements', options_list=('-p',), metavar='requirements.txt', default='', help='A pip requirements.txt file needed by the code file.', required=False)
# Registered model params
register_cli_argument('ml manifest create', 'model_ids', options_list=('-i', '--model-id'), help='Id of previously registered model to add to manifest. Multiple models can be specified with additional -i arguments', metavar='model_id', action='append', default=[], required=False, arg_group='Registered Model')
# Unregistered model params
register_cli_argument('ml manifest create', 'model_name', options_list=('-n', '--model-name'), help='Name of model to add to manifest. Can either be previously registered, or combined with a model file to register a new model.', required=False, arg_group='Unregistered Model')
register_cli_argument('ml manifest create', 'model_file', options_list=('-m', '--model-file'), help='Model file to register. If used, must be combined with model name.', required=False, arg_group='Unregistered Model')
register_cli_argument('ml manifest show', 'manifest_id', options_list=('-i', '--manifest-id'), help='Id of manifest to show')

# image workflows
register_cli_argument('ml image create', 'image_type', options_list=('--image-type'), help='The image type to create. Defaults to "Docker".', default='Docker', required=False)
register_cli_argument('ml image create', 'image_description', options_list=('--image-description'), help='Description of the image.', required=False)
# Registered manifest params
register_cli_argument('ml image create', 'manifest_id', options_list=('--manifest-id'), help='Id of previously registered manifest to use in image creation.', required=False, arg_group='Registered Manifest')
# Unregistered manifest params
register_cli_argument('ml image create', 'driver_file', options_list=('-f'), help='The code file to be deployed.', required=False, arg_group='Unregistered Manifest')
register_cli_argument('ml image create', 'schema_file', options_list=('-s', '--schema-file'), default='', help='Schema file to add to the manifest', required=False, arg_group='Unregistered Manifest')
register_cli_argument('ml image create', 'dependencies', options_list=('-d', '--dependency'), action='append', default=[], help='Files and directories required by the service. Multiple dependencies can be specified with additional -d arguments.', required=False, arg_group='Unregistered Manifest')
register_cli_argument('ml image create', 'runtime', options_list=('-r',), help='Runtime of the web service. Valid runtimes are {}'.format('|'.join(SUPPORTED_RUNTIMES)), required=False, arg_group='Unregistered Manifest')
register_cli_argument('ml image create', 'requirements', options_list=('-p',), metavar='requirements.txt', default='', help='A pip requirements.txt file needed by the code file.', required=False, arg_group='Unregistered Manifest')
register_cli_argument('ml image create', 'model_name', options_list=('-n', '--model-name'), help='Name of model to add to manifest.', required=False, arg_group='Unregistered Manifest')
register_cli_argument('ml image create', 'model_file', options_list=('-m', '--model-file'), help='Model file to register.', required=False, arg_group='Unregistered Manifest')
register_cli_argument('ml image show', 'image_id', options_list=('-i', '--image-id'), help='Id of image to show')

# hostacct workflows
register_cli_argument('ml hostacct create', 'resource_group', options_list=('-g', '--resource-group'), help='Resource group to create the host account in.')
register_cli_argument('ml hostacct create', 'name', options_list=('-n', '--name'), help='Name of the host account')
register_cli_argument('ml hostacct create', 'location', options_list=('-l', '--location'), help='Resource location')
register_cli_argument('ml hostacct create', 'sku_name', options_list=('--sku-name'), help='Sku name. Valid names are {}'.format('|'.join(POSSIBLE_SKU_NAMES)))
register_cli_argument('ml hostacct create', 'sku_tier', options_list=('--sku-tier'), help='Sku tier. Valid tiers are {}'.format('|'.join(POSSIBLE_SKU_TIERS)))
register_cli_argument('ml hostacct create', 'tags', options_list=('-t', '--tags'), default='{}', help='Tags for the host account.', required=False)
register_cli_argument('ml hostacct create', 'description', options_list=('-d', '--description'), default='', help='Description of the host account.', required=False)
register_cli_argument('ml hostacct list', 'resource_group', options_list=('-g', '--resource-group'), help='List host accounts in this resource group. If omitted, will list all host accounts in current subscription.', required=False)
register_cli_argument('ml hostacct show', 'resource_group', options_list=('-g', '--resource-group'), help='Resource group containing the host account to show. If ommited the currently set host account will be shown.', required=False)
register_cli_argument('ml hostacct show', 'name', options_list=('-n', '--name'), help='Name of host account to show. If ommited the currently set host account will be shown.', required=False)
register_cli_argument('ml hostacct update', 'resource_group', options_list=('-g', '--resource-group'), help='Resource group containing the host account to update.')
register_cli_argument('ml hostacct update', 'name', options_list=('-n', '--name'), help='Name of host account to update.')
register_cli_argument('ml hostacct update', 'sku_name', options_list=('--sku-name'), help='Sku name. If name is provided tier must also be provided. Valid names are {}'.format('|'.join(POSSIBLE_SKU_NAMES)), required=False)
register_cli_argument('ml hostacct update', 'sku_tier', options_list=('--sku-tier'), help='Sku tier If tier is provided name must also be provided. Valid tiers are {}'.format('|'.join(POSSIBLE_SKU_TIERS)), required=False)
register_cli_argument('ml hostacct update', 'tags', options_list=('-t', '--tags'), help='Tags for the host account.', required=False)
register_cli_argument('ml hostacct update', 'description', options_list=('-d', '--description'), help='Description of the host account.', required=False)
register_cli_argument('ml hostacct delete', 'resource_group', options_list=('-g', '--resource-group'), help='Resource group containing the host account to delete.')
register_cli_argument('ml hostacct delete', 'name', options_list=('-n', '--name'), help='Name of the host account to delete.')
register_cli_argument('ml hostacct set', 'resource_group', options_list=('-g', '--resource-group'), help='Resource group containing the host account to set.')
register_cli_argument('ml hostacct set', 'name', options_list=('-n', '--name'), help='Name of host account to set.')
