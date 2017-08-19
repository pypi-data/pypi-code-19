# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

#pylint: disable=line-too-long

from azure.cli.core.commands import client_factory
from ._constants import MLC_MODELS_PATH
from ._constants import MLC_CLIENT_PATH
from importlib import import_module
from azure.cli.core.util import CLIError
from ._transformers import transform_mlc_resource
from ._transformers import transform_mlc_resource_list
from ._aml_help_formatter import AmlHelpFormatter
from azure.cli.command_modules.ml.commands_utility import load_commands
from azure.cli.command_modules.ml.all_parameters import register_command_arguments
from msrestazure.azure_exceptions import CloudError
from msrest.exceptions import HttpOperationError

# Every command has several parts:
#
# 1. Commands [Add your command to ALL_COMMANDS so that it gets added. Optional arguments for
# registration (such as table_transformer) that must be provided to "cli_command" should be
# included as part of the dictionary in ALL_COMMANDS. Otherwise, add an empty dictionary.]
#
# 2. Command Information [Create a new key for your command in command_details.json.
# This will contain its name, the command itself, the command function/pointer, and arguments.]
#
# 3. Arguments [Should be added as part of the command_details.json file. See other commands for examples.]
#
# 4. Module [Functions called by the commands, make sure to specify their name when
# creating the command.]
#
# 5. Help [Warning: Help is not in this file! Make sure to update _help.py,
# which is under the same directory, with the new commands.]

mlc_client = import_module(MLC_CLIENT_PATH, package=__package__)
MachineLearningComputeManagementClient = mlc_client.MachineLearningComputeManagementClient

mlc_models = import_module(MLC_MODELS_PATH, package=__package__)
ErrorResponseException = mlc_models.ErrorResponseException


def factory(kwargs): return client_factory.get_mgmt_service_client(
    MachineLearningComputeManagementClient).operationalization_clusters


def _handle_exceptions(exc):
    if isinstance(exc, CLIError):
        raise exc
    elif isinstance(exc, HttpOperationError):
        if exc and exc.inner_exception and exc.inner_exception.details:
            raise CLIError('{}: {}'.format(exc.inner_exception.code,
                                           exc.inner_exception.details[0].message))
        if exc is not None and exc.response is not None:
            resp = exc.response.json()['error']
            raise CLIError('{}: {}'.format(resp['code'], resp['message']))

        raise CLIError(exc)
    elif isinstance(exc, CloudError):
        raise CLIError(exc)
    elif isinstance(exc, ErrorResponseException):
        raise CLIError(exc)
    raise exc


ALL_COMMANDS = {
    # "ml service create batch": {"formatter_class": AmlHelpFormatter},
    # "ml service run batch": {"formatter_class": AmlHelpFormatter},
    # "ml service list batch": {},
    # "ml service show batch": {},
    # "ml service delete batch": {},
    # "ml service showjob batch": {},
    # "ml service listjobs batch": {},
    # "ml service canceljob batch": {},

    "ml env cluster": {},
    "ml env show": {"exception_handler": _handle_exceptions,
                        "transform": transform_mlc_resource},
    "ml env local": {},
    "ml env setup": {"exception_handler": _handle_exceptions},
    "ml env list": {"client_factory": factory,
                    "transform": transform_mlc_resource_list},
    "ml env delete": {'exception_handler': _handle_exceptions},
    "ml env set": {},
    "ml env get-credentials": {"client_factory": factory,
                               "exception_handler": _handle_exceptions},

    "ml service create realtime": {},
    "ml service list realtime": {},
    "ml service show realtime": {},
    "ml service delete realtime": {},
    "ml service run realtime": {},
    "ml service scale realtime": {},
    "ml service update realtime": {},
    'ml service keys realtime': {},

    "ml model register": {},
    "ml model show": {},
    "ml model list": {},

    "ml manifest create": {},
    "ml manifest show": {},
    "ml manifest list": {},

    "ml image create": {},
    "ml image show": {},
    "ml image list": {},

    "ml account modelmanagement create": {},
    "ml account modelmanagement show": {},
    "ml account modelmanagement list": {},
    "ml account modelmanagement update": {},
    "ml account modelmanagement delete": {},
    "ml account modelmanagement set": {}
}

load_commands(ALL_COMMANDS)

for command in ALL_COMMANDS:
    register_command_arguments(command)
