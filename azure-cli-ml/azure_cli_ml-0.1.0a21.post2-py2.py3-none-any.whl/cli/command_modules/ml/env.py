import time
import types
from collections import OrderedDict
from builtins import input
from builtins import next
from azure.cli.core.util import CLIError
from ._util import CommandLineInterfaceContext
from ._util import InvalidConfError
from ._util import write_variables_to_amlenvrc
from ._az_util import AzureCliError
from ._az_util import az_get_app_insights_account
from ._az_util import validate_env_name
from ._az_util import InvalidNameError
from ._az_util import az_login
from ._az_util import az_check_subscription
from ._az_util import az_create_resource_group
from ._az_util import az_create_storage_and_acr
from ._az_util import az_create_app_insights_account
from ._az_util import query_deployment_status
from ..ml import __version__
from ._constants import MODE_KEY
from ._constants import LOCAL
import azure.cli.core.azlogging as azlogging
from ._constants import MLC_CLIENT_ENUMS_PATH
from .compute import compute_create
from importlib import import_module
mlc_client_enums = import_module(MLC_CLIENT_ENUMS_PATH, package=__package__)
OperationStatus = mlc_client_enums.OperationStatus
logger = azlogging.get_az_logger(__name__)


def version():
    print('Azure Machine Learning Command Line Tools {}'.format(__version__))


def env_cluster(verb, context=CommandLineInterfaceContext(), quiet=False):
    """[DEPRECATED] Switches environment to cluster mode."""
    logger.warning('This is a deprecated command. Instead, run:')
    logger.warning('  az ml env set -g <resource group> -n <cluster name>')
    logger.warning('If you have not yet provisioned an ML compute resource, you can do so with:')
    logger.warning('  az ml env setup -n <cluster name>')


def env_describe(context=CommandLineInterfaceContext()):
    """Print current environment settings."""
    if context.in_local_mode():
        print("")
        print("** Warning: Running in local mode. **")
        print("If running against an MLC resource, run against cluster with:\n"
              "  az ml env set -n <resource_name> -g <resource_group> ")
        print("")

    print('Storage account name   : {}'.format(context.az_account_name))
    print('Storage account key    : {}'.format(context.az_account_key))
    print('ACR URL                : {}'.format(context.acr_home))
    print('ACR username           : {}'.format(context.acr_user))
    print('ACR password           : {}'.format(context.acr_pw))
    print('App Insights account   : {}'.format(context.app_insights_account_name))
    print('App Insights key       : {}'.format(context.app_insights_account_key))


def env_local(verb, context=CommandLineInterfaceContext(), quiet=False):
    """
    Switch to local mode
    :param verb:
    :param context:
    :param quiet:
    :return:
    """

    try:
        conf = context.read_config()
        if not conf:
            if verb:
                print('[Debug] No configuration file found.')
            conf = {}
        elif MODE_KEY not in conf and verb:
            print('[Debug] No mode setting found in config file. Suspicious.')
        conf[MODE_KEY] = LOCAL
    except InvalidConfError:
        if verb:
            print('[Debug] Suspicious content in ~/.amlconf.')
            print('[Debug] Resetting.')
        conf = {MODE_KEY: LOCAL}

    context.write_config(conf)
    if not quiet:
        env_describe(context)
    return


def env_setup(name, cluster, service_principal_app_id,
              service_principal_password, location=None, resource_group=None,
              agent_count=2, yes=False, context=CommandLineInterfaceContext()):
    """
    Sets up an MLC environment.
    :param name:
    :param cluster:
    :param service_principal_app_id:
    :param service_principal_password:
    :param location:
    :param resource_group:
    :param agent_count:
    :param yes: bool Run without interaction. Will fail if not logged in.
    :param context:
    :return:
    """
    if not name:
        root_name = input('Enter environment name (1-20 characters, lowercase alphanumeric): ')
        try:
            validate_env_name(root_name)
        except InvalidNameError as e:
            print('Invalid environment name. {}'.format(e.message))
            return
    else:
        root_name = name

    if cluster:
        return compute_create(root_name, service_principal_app_id,
                              service_principal_password, location, resource_group,
                              agent_count, yes, context)

    print('Setting up your Azure ML environment with a storage account, App Insights account, and ACR registry.')
    if service_principal_app_id and not service_principal_password:
        raise CLIError('When deploying with service principal, password (-p) must be specified.')

    az_login(yes=yes)
    az_check_subscription(yes=yes, context=context)
    resource_group = az_create_resource_group(context, root_name)

    try:
        app_insight_values_to_check = OrderedDict([
                ('App Insights Account Name', context.app_insights_account_name),
                ('App Insights Account Key', context.app_insights_account_key)
            ])

    except CLIError:
        app_insight_values_to_check = {'__no_prompt__': None}

    app_insight_args = [root_name, resource_group]
    app_insights_deployment_id = create_action_with_prompt_if_defined(
        context,
        'App Insights Account',
        app_insight_values_to_check,
        az_create_app_insights_account,
        app_insight_args
    )

    try:
        acr_values_to_check = OrderedDict([
            ('ACR Login Server', context.acr_home),
            ('ACR Username', context.acr_user),
            ('ACR Password', context.acr_pw),
            ('Storage Account', context.az_account_name),
            ('Storage Key', context.az_account_key)]
        )
    except CLIError:
        acr_values_to_check = {'__no_prompt__': None}

    acr_args = [root_name, resource_group]
    (acr_login_server, context.acr_username, acr_password, storage_account_name,
     storage_account_key) = create_action_with_prompt_if_defined(
        context,
        'ACR and storage',
        acr_values_to_check,
        az_create_storage_and_acr,
        acr_args
    )

    env_statements = {}

    if isinstance(app_insights_deployment_id, types.GeneratorType):
        env_statements['AML_APP_INSIGHTS_NAME'] = next(app_insights_deployment_id)
        env_statements['AML_APP_INSIGHTS_KEY'] = next(app_insights_deployment_id)

    else:
        completed_deployment = None
        while not completed_deployment:
            try:
                print('Querying App Insights deployment...')
                completed_deployment = query_deployment_status(resource_group, app_insights_deployment_id)
                time.sleep(5)
            except AzureCliError as exc:
                print(exc.message)
                break
        if completed_deployment:
            app_insights_account_name, app_insights_account_key = az_get_app_insights_account(completed_deployment)
            env_statements['AML_APP_INSIGHTS_NAME'] = app_insights_account_name
            env_statements['AML_APP_INSIGHTS_KEY'] = app_insights_account_key

    print('To configure az ml for local use with this environment, set the following environment variables.')

    env_statements['AML_STORAGE_ACCT_NAME'] = storage_account_name
    env_statements['AML_STORAGE_ACCT_KEY'] = storage_account_key
    env_statements['AML_ACR_HOME'] = acr_login_server
    env_statements['AML_ACR_USER'] = context.acr_username
    env_statements['AML_ACR_PW'] = acr_password
    env_statements['AML_ROOT_NAME'] = root_name

    write_variables_to_amlenvrc(context, env_statements, 'w+')

    print('')


def create_action_with_prompt_if_defined(context, action_str, env_dict, action, action_args):
    prompt = True
    for key in env_dict:
        if not env_dict[key]:
            prompt = False
            break
    if prompt:
        print('Found existing {} set up.'.format(action_str))
        for key in env_dict:
            print('{0:30}: {1}'.format(key, env_dict[key]))
        answer = context.get_input('Set up a new {} instead (y/N)?'.format(action_str))
        if answer != 'y' and answer != 'yes':
            print('Continuing with configured {}.'.format(action_str))
            return (env_dict[key] for key in env_dict)
        else:
            return action(*action_args)
    return action(*action_args)
