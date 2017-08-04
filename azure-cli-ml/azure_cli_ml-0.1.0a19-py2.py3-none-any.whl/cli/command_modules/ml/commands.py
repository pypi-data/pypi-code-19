# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

#pylint: disable=line-too-long

from azure.cli.core.commands import cli_command
from ._aml_help_formatter import AmlHelpFormatter

# batch commands
cli_command(__name__, 'ml service create batch', 'azure.cli.command_modules.ml.service.batch#batch_service_create')
cli_command(__name__, 'ml service run batch', 'azure.cli.command_modules.ml.service.batch#batch_service_run')
cli_command(__name__, 'ml service list batch', 'azure.cli.command_modules.ml.service.batch#batch_service_list')
cli_command(__name__, 'ml service show batch', 'azure.cli.command_modules.ml.service.batch#batch_service_show')
cli_command(__name__, 'ml service delete batch', 'azure.cli.command_modules.ml.service.batch#batch_service_delete')
cli_command(__name__, 'ml service showjob batch', 'azure.cli.command_modules.ml.service.batch#batch_show_job')
cli_command(__name__, 'ml service listjobs batch', 'azure.cli.command_modules.ml.service.batch#batch_list_jobs')
cli_command(__name__, 'ml service canceljob batch', 'azure.cli.command_modules.ml.service.batch#batch_cancel_job')

# env commands
cli_command(__name__, 'ml env about', 'azure.cli.command_modules.ml.env#env_about')
cli_command(__name__, 'ml env cluster', 'azure.cli.command_modules.ml.env#env_cluster')
cli_command(__name__, 'ml env show', 'azure.cli.command_modules.ml.env#env_describe')
cli_command(__name__, 'ml env local', 'azure.cli.command_modules.ml.env#env_local')
cli_command(__name__, 'ml env setup', 'azure.cli.command_modules.ml.env#env_setup')

# realtime commands
cli_command(__name__, 'ml service create realtime', 'azure.cli.command_modules.ml.service.realtime#realtime_service_create')
cli_command(__name__, 'ml service list realtime', 'azure.cli.command_modules.ml.service.realtime#realtime_service_list')
cli_command(__name__, 'ml service show realtime', 'azure.cli.command_modules.ml.service.realtime#realtime_service_show')
cli_command(__name__, 'ml service delete realtime', 'azure.cli.command_modules.ml.service.realtime#realtime_service_delete')
cli_command(__name__, 'ml service run realtime', 'azure.cli.command_modules.ml.service.realtime#realtime_service_run')
cli_command(__name__, 'ml service scale realtime', 'azure.cli.command_modules.ml.service.realtime#realtime_service_scale')
cli_command(__name__, 'ml service update realtime', 'azure.cli.command_modules.ml.service.realtime#realtime_service_update')

# model commands
cli_command(__name__, 'ml model register', 'azure.cli.command_modules.ml.model#model_register')
cli_command(__name__, 'ml model show', 'azure.cli.command_modules.ml.model#model_show')
cli_command(__name__, 'ml model list', 'azure.cli.command_modules.ml.model#model_list')

# manifest commands
cli_command(__name__, 'ml manifest create', 'azure.cli.command_modules.ml.manifest#manifest_create')
cli_command(__name__, 'ml manifest show', 'azure.cli.command_modules.ml.manifest#manifest_show')
cli_command(__name__, 'ml manifest list', 'azure.cli.command_modules.ml.manifest#manifest_list')

# image commands
cli_command(__name__, 'ml image create', 'azure.cli.command_modules.ml.image#image_create')
cli_command(__name__, 'ml image show', 'azure.cli.command_modules.ml.image#image_show')
cli_command(__name__, 'ml image list', 'azure.cli.command_modules.ml.image#image_list')

# hostacct commands
cli_command(__name__, 'ml hostacct create', 'azure.cli.command_modules.ml.host_account#host_account_create')
cli_command(__name__, 'ml hostacct show', 'azure.cli.command_modules.ml.host_account#host_account_show')
cli_command(__name__, 'ml hostacct list', 'azure.cli.command_modules.ml.host_account#host_account_list')
cli_command(__name__, 'ml hostacct update', 'azure.cli.command_modules.ml.host_account#host_account_update')
cli_command(__name__, 'ml hostacct delete', 'azure.cli.command_modules.ml.host_account#host_account_delete')
cli_command(__name__, 'ml hostacct set', 'azure.cli.command_modules.ml.host_account#host_account_set')
