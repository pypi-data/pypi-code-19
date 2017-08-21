# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------


"""
Realtime services functions.

"""

from __future__ import print_function

import json
import os
import os.path
import time
import requests
import tabulate
import yaml
import sys
from pkg_resources import resource_string
import docker

from azure.cli.core.util import CLIError

from ..image import _image_create
from ..image import _image_show
from ._docker_utils import get_docker_client
from ._realtimeutilities import get_sample_data
from ._realtimeutilities import realtime_show_service_header_to_fn_dict
from ._realtimeutilities import realtime_show_service_details_header_to_fn_dict
from ._realtimeutilities import realtime_list_service_header_to_fn_dict
from .._k8s_util import K8sConstants
from .._k8s_util import KubernetesOperations
from .._k8s_util import check_for_kubectl
from .._k8s_util import get_k8s_realtime_frontend_url
from .._constants import SWAGGER_URI_FORMAT
from .._constants import DEFAULT_INPUT_DATA
from .._constants import SERVICE_DATA_DIRECTORY
from .._constants import SCORING_URI_FORMAT
from .._util import cli_context
from .._util import create_docker_image
from .._util import get_auth_header
from .._util import get_json
from .._util import get_current_model_management_url_base
from .._util import get_success_and_resp_str
from .._util import MultiTableResponse
from .._util import PaginatedTableResponse
from .._util import add_sdk_to_requirements
from .._util import wrap_driver_file
from .._util import poll_mms_async_operation

from kubernetes.client.rest import ApiException
from .._constants import MLC_RESOURCE_ID_FMT
from .._constants import MMS_API_VERSION
from .._constants import MMS_SERVICE_URL_ENDPOINT
from .._constants import MMS_SERVICE_LIST_KEYS_URL_ENDPOINT
from .._constants import MMS_SERVICE_REGEN_KEYS_URL_ENDPOINT
from .._constants import MMS_OPERATION_URL_ENDPOINT
from .._constants import MMS_SERVICE_CREATE_OPERATION_POLLING_MAX_TRIES
from .._constants import MMS_SYNC_TIMEOUT_SECONDS
from .._constants import SUCCESS_RETURN_CODE
from .._constants import USER_ERROR_RETURN_CODE

# Local mode functions


def realtime_service_delete_local(service_name, verbose):
    """Delete a locally published realtime web service."""
    client = get_docker_client()
    try:
        containers = client.containers.list(filters={'label': 'amlid={}'.format(service_name)})
    except docker.errors.DockerException as exc:
        raise CLIError('Unable to list containers: {}'.format(exc))
    if not containers:
        print("[Local mode] Error: no service named {} running locally.".format(service_name))
        print("[Local mode] To delete a cluster based service, switch to remote mode first: az ml env remote")
        return
    if len(containers) != 1:
        print("[Local mode] Error: ambiguous reference - too many containers ({}) with the same label.".format(
            len(containers)))
        return
    container = containers[0]
    container_id = container.attrs['Id'][0:12]
    if verbose:
        print("Killing docker container id {}".format(container_id))
    image_name = container.attrs['Config']['Image']
    try:
        container.kill()
        container.remove()
        client.images.remove(image_name, force=True)
    except docker.errors.DockerException as exc:
        raise CLIError('Unable to properly remove service: {}'.format(exc))
    print("Service deleted.")
    return SUCCESS_RETURN_CODE


def get_local_realtime_service_port(service_name, verbose):
    """Find the host port mapping for a locally published realtime web service."""

    client = get_docker_client()
    try:
        containers = client.containers.list(filters={'label': 'amlid={}'.format(service_name)})
    except docker.errors.DockerException as exc:
        raise CLIError('Unable to list docker containers: {}'.format(str(exc)))
    if len(containers) == 1:
        container = containers[0]
        port_info_dict = container.attrs['NetworkSettings']['Ports']
        for key in port_info_dict:
            if '5001' in key and len(port_info_dict[key]) == 1:
                port = port_info_dict[key][0]['HostPort']
                if verbose:
                    print('Container port: {}'.format(port))
                return port
        raise CLIError('Unable to locate expected port info in Ports '
                       'dictionary: {}'.format(port_info_dict))
    raise CLIError('Expected exactly one container with label {} and found {}.'.format(
        'amlid={}'.format(service_name), len(containers)))


def realtime_service_deploy_local(context, service_label, image, verbose, app_insights_enabled, model_data_collection_enabled):
    """Deploy a realtime web service locally as a docker container."""

    print("[Local mode] Running docker container.")

    # Delete any local containers with the same label
    try:
        existing_container_port = get_local_realtime_service_port(service_label, verbose)
        print('Found existing local service with the same name running at http://127.0.0.1:{}/score'
              .format(existing_container_port))
        answer = context.get_input('Delete existing service and create new service (y/N)? ')
        answer = answer.rstrip().lower()
        if answer != 'y' and answer != 'yes':
            print('Canceling service create.')
            return 1
        realtime_service_delete_local(service_label, verbose)
    except CLIError:
        # note - we swallow this error here, but may see it again below.
        pass

    client = get_docker_client()
    try:
        print('[Local mode] Pulling the image from {}. '
              'This may take a few minutes, depending on your connection speed...'.format(image))
        sys.stdout.write('[Local mode] Pulling')
        num_lines = 0
        for outer_line in client.api.pull(image, stream=True, auth_config={
            'username': context.acr_user,
            'password': context.acr_pw
        }):
            # stream sometimes sends multiple lines as one "line," despite documentation
            num_lines += outer_line.decode().count('\n')
            while num_lines > 10:
                sys.stdout.write('.')
                sys.stdout.flush()
                num_lines -= 10
        print('')
    except docker.errors.DockerException as exc:
        raise CLIError('Unable to pull image {}: {}'.format(image, exc))
    container_env = {'AML_APP_INSIGHTS_KEY': context.app_insights_account_key,
                     'AML_APP_INSIGHTS_ENABLED': app_insights_enabled,
                     'AML_MODEL_DC_STORAGE_ENABLED': model_data_collection_enabled,
                     'AML_MODEL_DC_EVENT_HUB_ENABLED': 'false',
                     'AML_MODEL_DC_STORAGE': context.model_dc_storage,
                     'AML_MODEL_DC_EVENT_HUB': context.model_dc_event_hub}
    container_labels = {'amlid': service_label}
    try:
        client.containers.run(image,
                              environment=container_env,
                              detach=True,
                              publish_all_ports=True,
                              labels=container_labels)
    except docker.errors.DockerException as exc:
        raise CLIError('Unable to start container: {}'.format(exc))

    # above container does not contain full port info--fetch it
    try:
        dockerport = get_local_realtime_service_port(service_label, verbose)
    except CLIError:
        print('[Local mode] Failed to start container. Please report this to deployml@microsoft.com with your image id: {}'.format(image)) #pylint: disable=line-too-long
        raise

    # Wait for the in container server to boot up before making a call for sample data
    time.sleep(10)
    swagger_url = SWAGGER_URI_FORMAT.format("http://127.0.0.1:{}".format(dockerport))
    input_data = get_sample_data(swagger_url, verbose=verbose)
    if not input_data:
        input_data = DEFAULT_INPUT_DATA
    print("[Local mode] Success.")
    print('[Local mode] Scoring endpoint: http://127.0.0.1:{}/score'.format(dockerport))
    formatted_sample = str(input_data).replace("\'", "\\\"")
    print("[Local mode] Usage: az ml service run realtime -n " + service_label + " -d \"{}\"".format(formatted_sample))
    return SUCCESS_RETURN_CODE


def realtime_service_run_local(service_name, input_data, verbose):
    """Run a previously published local realtime web service."""

    try:
        container_port = get_local_realtime_service_port(service_name, verbose)
    except CLIError:
        print("[Local mode] No service named {} running locally.".format(service_name))
        print("To run a remote service, switch environments using: az ml env remote")
        raise
    else:
        headers = {'Content-Type': 'application/json'}
        if input_data == '':
            print("No input data specified. Checking for sample data.")
            swagger_url = SWAGGER_URI_FORMAT.format("http://127.0.0.1:{}".format(container_port))
            input_data = get_sample_data(swagger_url, headers, verbose)
            if not input_data:
                print(
                    "No sample data available. To score with your own data, run: az ml service run realtime -n {} -d \"<input_data>\"" #pylint: disable=line-too-long
                    .format(service_name))
                return
            print('Using sample data: ' + input_data)
        else:
            if verbose:
                print('[Debug] Input data is {}'.format(input_data))
                print('[Debug] Input data type is {}'.format(type(input_data)))

        service_url = 'http://127.0.0.1:{}/score'.format(container_port)
        if verbose:
            print("Service url: {}".format(service_url))
        try:
            result = requests.post(service_url, headers=headers, data=input_data, verify=False)
        except requests.ConnectionError:
            print('[Local mode] Error connecting to container. Please try recreating your local service.')
            return

        if verbose:
            print(result.content)

        if result.status_code == 200:
            result = result.json()
            print(result)
            return SUCCESS_RETURN_CODE
        else:
            print(result.content)

# Cluster mode functions

def realtime_service_scale(service_name, num_replicas, context=cli_context):
    _realtime_service_scale(service_name, num_replicas, context)


def _realtime_service_scale(service_name, num_replicas, context=cli_context):
    """Scale a published realtime web service."""
    if context.in_local_mode():
        print("Error: Scaling is not supported in local mode.")
        print("To scale a cluster based service, switch to cluster mode first: az ml env cluster")
        return SUCCESS_RETURN_CODE

    try:
        if num_replicas < 1 or num_replicas > 17:
            raise ValueError
    except ValueError:
        print("The -z option must be an integer in range [1-17] inclusive.")
        return

    if not check_for_kubectl(context):
        print('')
        print('kubectl is required to scale webservices. Please install it on your path and try again.')
        return

    ops = KubernetesOperations(context)
    ops.scale_deployment(service_name, num_replicas, context)
    return SUCCESS_RETURN_CODE


def realtime_service_delete_kubernetes(context, service_name, verbose):
    k8s_ops = KubernetesOperations(context)
    try:
        if not check_for_kubectl(context):
            print('')
            print('kubectl is required to delete webservices. Please install it on your path and try again.')
            return
        k8s_ops.delete_service(service_name)
        k8s_ops.delete_deployment(service_name, context)
        return SUCCESS_RETURN_CODE
    except ApiException as exc:
        if exc.status == 404:
            print("Unable to find web service with name {}.".format(service_name))
            return
        print("Exception occurred while trying to delete service {}. {}".format(service_name, exc))


def realtime_service_delete(service_name, service_id, verb, context=cli_context):
    _realtime_service_delete(service_name, service_id, verb, context)


def _realtime_service_delete(service_name, service_id, verb, context=cli_context):
    """Delete a realtime web service."""
    if context.in_local_mode():
        if service_id and not service_name:
            service_name = service_id.split('.')[0]
        return realtime_service_delete_local(service_name, verb)

    if service_id:
        return _mms_service_delete(service_id, verb, context)
    else:
        return realtime_service_delete_kubernetes(context, service_name, verb)


def realtime_service_create(driver_file, dependencies, requirements, schema_file, service_name, custom_ice_url,
                            target_runtime, app_insights_logging_enabled, model_data_collection_enabled, model_file,
                            num_replicas, image_id, image_type, conda_file, verb, context=cli_context, use_ice=False):
    _realtime_service_create(driver_file, dependencies, requirements, schema_file, service_name, custom_ice_url,
                             target_runtime, app_insights_logging_enabled, model_data_collection_enabled, model_file,
                             num_replicas, image_id, image_type, conda_file, verb, context, use_ice)


# Currently, mms doesn't take options for requirements, custom_ice_url, app_insights_logging_enabled,
# model_data_collection_enabled, and num_replicas
def _realtime_service_create(driver_file, dependencies, requirements, schema_file, service_name, custom_ice_url,
                             target_runtime, app_insights_logging_enabled, model_data_collection_enabled, model_file,
                             num_replicas, image_id, image_type, conda_file, verb, context=cli_context, use_ice=False):
    if not use_ice:
        return _mms_service_create(image_id, image_type, service_name, driver_file, model_file, schema_file,
                                   dependencies, target_runtime, requirements, app_insights_logging_enabled,
                                   model_data_collection_enabled, num_replicas, verb, context)
    else:
        """Create a new realtime web service."""

        requirements = add_sdk_to_requirements(requirements)

        # wrap user driver
        if not driver_file:
            raise CLIError('Driver filepath must be provided with -f argument.')
        wrapped_driver_file = wrap_driver_file(driver_file, schema_file, dependencies)
        app_insights_enabled = str(bool(app_insights_logging_enabled)).lower()
        model_data_collection_enabled = str(bool(model_data_collection_enabled)).lower()

        image = create_docker_image(wrapped_driver_file, dependencies, service_name, verb,
                                    target_runtime, context, requirements, schema_file,
                                    model_file, custom_ice_url, conda_file)

        if image is None:
            return

        if context.in_local_mode():
            service_label = image.split("/")[1]
            return realtime_service_deploy_local(context, service_label, image, verb, app_insights_enabled, model_data_collection_enabled)

        return realtime_service_deploy_k8s(context, image, service_name, app_insights_enabled, model_data_collection_enabled, num_replicas, verb)


def realtime_service_deploy_k8s(context, image, app_id, app_insights_enabled, model_data_collection_enabled, num_replicas, verbose=False):
    """Deploy a realtime Kubernetes web service from a docker image."""

    k8s_template_path = os.path.join(SERVICE_DATA_DIRECTORY, 'kubernetes_deployment_template.yaml')
    k8s_service_template_path = os.path.join(SERVICE_DATA_DIRECTORY, 'kubernetes_service_template.yaml')
    num_replicas = int(num_replicas)

    try:
        with open(k8s_template_path) as f:
            kubernetes_app = yaml.load(f)
    except OSError as exc:
        print("Unable to find kubernetes deployment template file.".format(exc))
        raise
    kubernetes_app['metadata']['name'] = app_id
    kubernetes_app['spec']['replicas'] = num_replicas
    kubernetes_app['spec']['template']['spec']['containers'][0]['image'] = image
    kubernetes_app['spec']['template']['spec']['containers'][0]['name'] = app_id
    kubernetes_app['spec']['template']['metadata']['labels']['webservicename'] = app_id
    kubernetes_app['spec']['template']['metadata']['labels']['azuremlappname'] = app_id
    kubernetes_app['spec']['template']['metadata']['labels']['type'] = "realtime"
    kubernetes_app['spec']['template']['spec']['containers'][0]['env'][0]['valueFrom'] = {'configMapKeyRef': {'name': app_id + '-config', 'key': 'appinsightskey' }}
    kubernetes_app['spec']['template']['spec']['containers'][0]['env'][1]['valueFrom'] = {'configMapKeyRef': {'name': app_id + '-config', 'key': 'appinsightsenabled' }}
    kubernetes_app['spec']['template']['spec']['containers'][0]['env'][4]['valueFrom'] = {'configMapKeyRef': {'name': app_id + '-config', 'key': 'modeldcstorageenabled' }}
    kubernetes_app['spec']['template']['spec']['containers'][0]['env'][5]['valueFrom'] = {'configMapKeyRef': {'name': app_id + '-config', 'key': 'modeldceventhubenabled' }}
    kubernetes_app['spec']['template']['spec']['imagePullSecrets'][0]['name'] = context.acr_user + 'acrkey'

    service_config_map = dict()
    service_config_map['modeldcstorageenabled'] = model_data_collection_enabled
    service_config_map['modeldceventhubenabled'] = 'false'
    service_config_map['appinsightskey'] = context.app_insights_account_key
    service_config_map['appinsightsenabled'] = app_insights_enabled

    if context.model_dc_storage and context.model_dc_event_hub:
        kubernetes_app['spec']['template']['spec']['containers'][0]['env'][2]['valueFrom'] = {'secretKeyRef': {'name': 'modeldckeys', 'key': 'storageaccount' }}
        kubernetes_app['spec']['template']['spec']['containers'][0]['env'][3]['valueFrom'] = {'secretKeyRef': {'name': 'modeldckeys', 'key': 'eventhub' }}

    k8s_ops = KubernetesOperations(context)
    timeout_seconds = 1200
    try:
        k8s_ops.add_service_config(app_id, service_config_map)
        # Move model data collection kube secret creation to webservice creation so existing environments can onboard to the feature.
        # Eventually, this will become a part of the Environment RP and move back to environment creation.
        if context.model_dc_storage and context.model_dc_event_hub:
            k8s_ops.add_model_dc_secret('modeldckeys', context.model_dc_storage, context.model_dc_event_hub)
        k8s_ops.deploy_deployment(kubernetes_app, timeout_seconds, num_replicas, context.acr_user + 'acrkey', verbose)
        k8s_ops.create_service(k8s_service_template_path, app_id, 'realtime', verbose)

        print("Success.")
        print("Usage: az ml service run realtime -n " + app_id + " -d \"" + DEFAULT_INPUT_DATA + "\"")
        return SUCCESS_RETURN_CODE

    except ApiException as exc:
        print("An exception occurred while deploying the service. {}".format(exc))


def realtime_service_show(service_name, service_id, verb=False, context=cli_context):
    _realtime_service_show(service_name, service_id, verb, context)


def _realtime_service_show(service_name, service_id, verb=False, context=cli_context):
    """show details of a previously published realtime web service."""

    if service_id and not context.in_local_mode():
        return _mms_service_show(service_id, verb, context)

    verbose = verb

    # First print the list view of this service
    num_services = get_webservices(service_name, verb, context)

    usage_headers = ['-H "Content-Type:application/json"']

    if context.in_local_mode():
        if service_id and not service_name:
            service_name = service_id.split('.')[0]
        client = get_docker_client()
        try:
            containers = client.containers.list(filters={'label': 'amlid={}'.format(service_name)})
        except docker.errors.DockerException as exc:
            raise CLIError('Unable to list containers: {}'.format(exc))

        if len(containers) != 1:
            print('[Local mode] Error retrieving container details.')
            print('[Local mode] Label should match exactly one container '
                  'and instead matched {}.'.format(len(containers)))
            return
        container = containers[0]
        ports = container.attrs['NetworkSettings']['Ports']
        scoring_port_key = [x for x in ports.keys() if '5001' in x]
        if len(scoring_port_key) != 1:
            print('[Local mode] Error: Malconfigured container. '
                  'Cannot determine scoring port.')
            return
        scoring_port = ports[scoring_port_key[0]][0]['HostPort']
        if scoring_port:
            service_host = 'http://127.0.0.1:' + str(scoring_port)
            scoring_url = SCORING_URI_FORMAT.format(service_host)
            swagger_url = SWAGGER_URI_FORMAT.format(service_host)
            headers = {'Content-Type': 'application/json'}
        else:
            print('[Local mode] Error: Misconfigured container. '
                  'Cannot determine scoring port.')
            return
    else:
        try:
            fe_url = get_k8s_realtime_frontend_url(context)
        except ApiException:
            return
        scoring_url = fe_url + service_name + '/score'
        swagger_url = fe_url + service_name + '/swagger.json'
        headers = {'Content-Type': 'application/json'}

    sample_data = get_sample_data(swagger_url, headers, verbose)
    if not sample_data:
        sample_data = DEFAULT_INPUT_DATA
    if num_services:
        print('Usage:')
        formatted_sample = str(sample_data).replace("\'", "\\\"")
        print('  az ml  : az ml service run realtime -n {} -d \"{}\"'.format(service_name, formatted_sample))
        print('  curl : curl -X POST {} --data \"{}\" {}'.format(' '.join(usage_headers), formatted_sample, scoring_url))
        return SUCCESS_RETURN_CODE


def realtime_service_list(service_name=None, use_ice=False, verb=False, context=cli_context):
    _realtime_service_list(service_name, use_ice, verb, context)


def _realtime_service_list(service_name=None, use_ice=False, verb=False, context=cli_context):
    if not use_ice and not context.in_local_mode():
        return _mms_service_list(verb, context)

    # all error paths return None--if we get anything that is not None, return SUCCESS
    return SUCCESS_RETURN_CODE if get_webservices(service_name, verb, context) is not None else None


def get_webservices(service_name=None, verb=False, context=cli_context):
    """List published realtime web services."""

    verbose = verb

    if context.in_local_mode():
        if service_name is not None:
            filters = {'label': 'amlid={}'.format(service_name)}
        else:
            filters = {'label': 'amlid'}

        client = get_docker_client()

        try:
            containers = client.containers.list(filters=filters)
            if not containers and service_name:
                raise CLIError('No service with name {} is running locally.'.format(service_name))
            app_table = [
                            ['NAME', 'IMAGE', 'CPU', 'MEMORY', 'STATUS', 'INSTANCES',
                             'HEALTH']
                        ] + [[
                                 container.attrs['Config']['Labels']['amlid'],
                                 container.attrs['Config'][
                                     'Image'] if 'Image' in container.attrs else 'Unknown',
                                 'N/A',  # CPU
                                 'N/A',  # Memory
                                 container.attrs['State']['Status'],
                                 1,  # Instances
                                 'N/A',  # health
                             ] for container in client.containers.list(filters=filters)
                             ]
        except docker.errors.DockerException as exc:
            raise CLIError('Unable to list containers: {}'.format(exc))

        print(tabulate.tabulate(app_table, headers='firstrow', tablefmt='psql'))

        return len(app_table) - 1
    # Cluster mode
    return realtime_service_list_kubernetes(context, service_name, verbose)


def realtime_service_list_kubernetes(context, service_name=None, verbose=False):
    label_selector = "type==realtime"
    if service_name is not None:
        label_selector += ",webservicename=={}".format(service_name)

    if verbose:
        print("label selector: {}".format(label_selector))

    try:
        k8s_ops = KubernetesOperations(context)
        list_result = k8s_ops.get_filtered_deployments(label_selector)
    except ApiException as exc:
        print("Failed to list deployments. {}".format(exc))
        return

    if verbose:
        print("Retrieved deployments: ")
        print(list_result)

    if len(list_result) > 0:
        app_table = [['NAME', 'IMAGE', 'STATUS', 'INSTANCES', 'HEALTH']]
        for app in list_result:
            app_image = app.spec.template.spec.containers[0].image
            app_name = app.metadata.labels['webservicename']
            app_status = app.status.conditions[0].type
            app_instances = app.status.replicas
            app_health = 'Healthy' if app.status.unavailable_replicas is None else 'Unhealthy'
            app_entry = [app_name, app_image, app_status, app_instances, app_health]
            app_table.append(app_entry)
        print(tabulate.tabulate(app_table, headers='firstrow', tablefmt='psql'))
        return len(app_table) - 1
    else:
        if service_name:
            raise CLIError('No service running with name {} on your ACS cluster'.format(service_name))
        else:
            print('No running services on your ACS cluster')
            return SUCCESS_RETURN_CODE


def realtime_service_run_kubernetes(context, service_name, service_id, input_data, verbose):
    scoring_headers = {'Content-Type': 'application/json'}

    if service_id:
        auth_header = get_auth_header()
        mms_headers = {'Authorization': auth_header}
        params = {'api-version': MMS_API_VERSION}
        service_url = get_current_model_management_url_base() + MMS_SERVICE_URL_ENDPOINT + '/{}'.format(service_id)
        input_data = json.dumps({"input": input_data})

        try:
            resp = context.http_call('get', service_url, params=params, headers=mms_headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
        except requests.ConnectionError:
            raise CLIError('Error connecting to {}.'.format(service_url))
        except requests.Timeout:
            raise CLIError('Error, request to {} timed out.'.format(service_url))

        if resp.status_code == 200:
            if verbose:
                print('Successfully got service to score against\nStatus Code: {}\nHeaders: {}\nContent: {}'.format(
                    resp.status_code, resp.headers, resp.content))
            endpoint_obj = get_json(resp.content, pascal=True)
            scoring_endpoint = endpoint_obj['ScoringUri']
        else:
            raise CLIError('Error occurred while attempting to retrieve service {} to score against.\nStatus Code: {}\nHeaders: {}\nContent: {}'.format(service_id, resp.status_code, resp.headers, resp.content))

        keys_url = service_url + '/keys'

        try:
            resp = context.http_call('get', keys_url, params=params, headers=mms_headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
        except requests.ConnectionError:
            raise CLIError('Error connecting to {}.'.format(service_url))
        except requests.Timeout:
            raise CLIError('Error, request to {} timed out.'.format(service_url))

        if resp.status_code == 200:
            if verbose:
                print('Successfully got keys for service\nStatus Code: {}\nHeaders: {}\nContent: {}'.format(resp.status_code, resp.headers, resp.content))
            service_keys = get_json(resp.content, pascal=True)
            scoring_headers['Authorization'] = 'Bearer {}'.format(service_keys['PrimaryKey'])
        else:
            raise CLIError('Error occurred while attempting to retrieve service keys.\nStatus Code: {}\nHeaders: {}\nContent: {}'.format(resp.status_code, resp.headers, resp.content))
    else:
        try:
            frontend_service_url = get_k8s_realtime_frontend_url(context)
        except ApiException as exc:
            print("Unable to connect to Kubernetes Front-End service. {}".format(exc))
            return
        if input_data is None:
            swagger_url = frontend_service_url + service_name + '/swagger.json'
            input_data = get_sample_data(swagger_url, scoring_headers, verbose)

        scoring_endpoint = frontend_service_url + service_name + '/score'

    result = requests.post(scoring_endpoint, data=input_data, headers=scoring_headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    if verbose:
        print('Got result from scoring request at {}.\nStatus Code: {}\nHeaders: {}\nContent: {}'.format(scoring_endpoint, result.status_code, result.headers, result.content))

    if not result.ok:
        print('Error scoring the service.')
        content = result.content.decode()
        if content == "ehostunreach":
            print('Unable to reach the requested host.')
            print('If you just created this service, it may not be available yet. Please try again in a few minutes.')
        elif '%MatchError' in content or 'No such thing' in content:
            print('Unable to find service with name {}.'.format(service_name))
        else:
            print(content)
        return

    try:
        result = result.json()
        print(result)
        return SUCCESS_RETURN_CODE
    except ValueError:
        print('Error scoring the service.')
        print(result.content)
        return
    

def realtime_service_run(service_name, service_id, input_data, verb, context=cli_context):
    _realtime_service_run(service_name, service_id, input_data, verb, context)


def _realtime_service_run(service_name, service_id, input_data, verb, context=cli_context):
    """
    Execute a previously published realtime web service.
    :param context: CommandLineInterfaceContext object
    :param args: list of str arguments
    """

    verbose = verb

    if verbose:
        print("data: {}".format(input_data))

    if context.in_local_mode():
        if service_id and not service_name:
            service_name = ''.join(service_id.split('.')[0])
        return realtime_service_run_local(service_name, input_data, verbose)

    return realtime_service_run_kubernetes(context, service_name, service_id, input_data, verbose)


def realtime_service_update(service_id, image_id, num_replicas, enable_model_data_collection,
                            disable_model_data_collection, verb, context=cli_context):
    _realtime_service_update(service_id, image_id, num_replicas, enable_model_data_collection,
                             disable_model_data_collection, verb, context)


def _realtime_service_update(service_id, image_id, num_replicas, enable_model_data_collection,
                             disable_model_data_collection, verb, context=cli_context):
    return _mms_service_update(service_id, image_id, num_replicas, enable_model_data_collection,
                               disable_model_data_collection, verb, context)


def realtime_service_keys_handling(service_id, regen, verb, context=cli_context):
    _realtime_service_keys_handling(service_id, regen, verb, context)


def _realtime_service_keys_handling(service_id, regen, verb, context=cli_context):
    auth_header = get_auth_header()
    headers = {'Content-Type': 'application/json', 'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}

    if regen:
        regen_keys_url = get_current_model_management_url_base() + MMS_SERVICE_REGEN_KEYS_URL_ENDPOINT.format(service_id)
        try:
            resp = context.http_call('post', regen_keys_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
        except requests.ConnectionError:
            raise CLIError('Error connecting to {}.'.format(regen_keys_url))
        except requests.Timeout:
            raise CLIError('Error, request to {} timed out.'.format(regen_keys_url))
    else:
        list_keys_url = get_current_model_management_url_base() + MMS_SERVICE_LIST_KEYS_URL_ENDPOINT.format(service_id)
        try:
            resp = context.http_call('get', list_keys_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
        except requests.ConnectionError:
            raise CLIError('Error connecting to {}.'.format(list_keys_url))
        except requests.Timeout:
            raise CLIError('Error, request to {} timed out.'.format(list_keys_url))

    if resp.status_code == 200:
        resp_obj = get_json(resp.content, pascal=True)
        try:
            primary_key = resp_obj['PrimaryKey']
        except KeyError:
            raise CLIError('Invalide response key: PrimaryKey')
        try:
            secondary_key = resp_obj['SecondaryKey']
        except KeyError:
            raise CLIError('Invalide response key: SecondaryKey')

        print('PrimaryKey: {}\nSecondaryKey: {}'.format(primary_key, secondary_key))
    else:
        if regen:
            action = 'regenerating'
        else:
            action = 'listing'
        raise CLIError('Error occurred while {} keys for service.\nStatus Code: {}\nHeaders: {}\nContent: {}'.format(action, resp.status_code, resp.headers, resp.content))


# MMS functions
def _mms_service_create(image_id, image_type, service_name, driver_file, model_file, schema_file,
                        dependencies, runtime, requirements, app_insights_logging_enabled,
                        model_data_collection_enabled, num_replicas, verb, context):
    auth_header = get_auth_header()
    headers = {'Content-Type': 'application/json', 'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}
    service_url = get_current_model_management_url_base() + MMS_SERVICE_URL_ENDPOINT

    if not image_id:
        image_create_success, image_id = _image_create(service_name[:30], image_type, '', None, driver_file, schema_file, dependencies,
                                                       runtime, requirements, model_file, verb, context)
        if image_create_success is not SUCCESS_RETURN_CODE:
            return

    if context.in_local_mode():
        result, image_details = _image_show(image_id, verb, context)
        if result != SUCCESS_RETURN_CODE:
            raise CLIError('Error, unable to retrieve information for {}.'.format(image_id))
        try:
            image_location = image_details['ImageLocation']
        except KeyError:
            raise CLIError('Error, unable to determine ImageLocation\n{}'.format(image_details))
        app_insights_logging_enabled = str(bool(app_insights_logging_enabled)).lower()
        model_data_collection_enabled = str(bool(model_data_collection_enabled)).lower()
        return realtime_service_deploy_local(context, service_name, image_location, verb, app_insights_logging_enabled, model_data_collection_enabled), service_name

    json_payload = json.loads(resource_string(__name__, 'data/mmsservicepayloadtemplate.json').decode('ascii'))
    json_payload['imageId'] = image_id
    json_payload['name'] = service_name
    json_payload['numReplicas'] = num_replicas
    json_payload['computeResource']['id'] = MLC_RESOURCE_ID_FMT.format(context.current_compute_subscription_id,
                                                                       context.current_compute_resource_group,
                                                                       context.current_compute_name)
    json_payload['dataCollection']['storageEnabled'] = model_data_collection_enabled
    json_payload['dataCollection']['eventHubEnabled'] = False

    if verb:
        print('Sending the following payload to {}\n{}'.format(service_url, json_payload))

    try:
        resp = context.http_call('post', service_url, params=params, headers=headers, json=json_payload, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}.'.format(service_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(service_url))

    if resp.status_code != 202:
        raise CLIError('Error occurred creating service.\nStatus Code: {}\nHeaders: {}\nContent: {}'.format(resp.status_code, resp.headers, resp.content))

    try:
        operation_location = resp.headers['Operation-Location']
    except KeyError:
        raise CLIError('Invalid response header key: Operation-Location')
    create_operation_status_id = operation_location.split('/')[-1]

    if verb:
        print('Operation Id: {}'.format(create_operation_status_id))

    operation_url = get_current_model_management_url_base() + MMS_OPERATION_URL_ENDPOINT.format(create_operation_status_id)
    operation_headers = {'Authorization': auth_header}

    sys.stdout.write('Creating service')
    sys.stdout.flush()
    service_id = poll_mms_async_operation(operation_url, operation_headers, params,
                                          MMS_SERVICE_CREATE_OPERATION_POLLING_MAX_TRIES, context)
    print('Done')
    print('Service ID: {}'.format(service_id))
    print("Usage: az ml service run realtime -i " + service_id + " -d \"" + DEFAULT_INPUT_DATA + "\"")
    return SUCCESS_RETURN_CODE, service_id


def _mms_service_show(service_id, verb, context):
    auth_header = get_auth_header()
    headers = {'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}
    service_url = get_current_model_management_url_base() + MMS_SERVICE_URL_ENDPOINT + '/{}'.format(service_id)

    try:
        resp = context.http_call('get', service_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}.'.format(service_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(service_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp,
                                       response_obj=MultiTableResponse([realtime_show_service_header_to_fn_dict,
                                                                        realtime_show_service_details_header_to_fn_dict]))[1])
        return SUCCESS_RETURN_CODE, get_json(resp.content, pascal=True)
    else:
        raise CLIError('Error occurred while attempting to show service {}.\nStatus Code: {}\nHeaders: {}\nContent: {}'.format(service_id, resp.status_code, resp.headers, resp.content))


def _mms_service_list(verb, context):
    auth_header = get_auth_header()
    headers = {'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}
    service_url = get_current_model_management_url_base() + MMS_SERVICE_URL_ENDPOINT

    try:
        resp = context.http_call('get', service_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}'.format(service_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(service_url))

    if resp.status_code == 200:
        print(get_success_and_resp_str(context, resp, response_obj=PaginatedTableResponse('Value', realtime_list_service_header_to_fn_dict))[1])
        return SUCCESS_RETURN_CODE
    else:
        raise CLIError('Error occurred while attempting to list services.\nStatus Code: {}\nHeaders: {}\nContent: {}'.format(resp.status_code, resp.headers, resp.content))


def _mms_service_delete(service_id, verb, context):
    auth_header = get_auth_header()
    headers = {'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}
    service_url = get_current_model_management_url_base() + MMS_SERVICE_URL_ENDPOINT + '/{}'.format(service_id)

    try:
        resp = context.http_call('delete', service_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}'.format(service_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(service_url))

    if resp.status_code == 200:
        print('Successfully deleted service: {}'.format(service_id))
        return SUCCESS_RETURN_CODE
    elif resp.status_code == 204:
        print('Service to delete {} not found.'.format(service_id))
        return SUCCESS_RETURN_CODE
    else:
        raise CLIError('Error occurred while attempting to delete service {}.\nStatus Code: {}\nHeaders: {}\nContent: {}'.format(service_id, resp.status_code, resp.headers, resp.content))


def _mms_service_update(service_id, image_id, num_replicas, enable_model_data_collection,
                        disable_model_data_collection, verb, context):
    auth_header = get_auth_header()
    headers = {'Content-Type': 'application/json', 'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}
    service_url = get_current_model_management_url_base() + MMS_SERVICE_URL_ENDPOINT + '/{}'.format(service_id)
    json_payload = json.loads(resource_string(__name__, 'data/mmsservicepayloadtemplate.json').decode('ascii'))
    del(json_payload['name'])
    json_payload['computeResource']['id'] = MLC_RESOURCE_ID_FMT.format(context.current_compute_subscription_id,
                                                                       context.current_compute_resource_group,
                                                                       context.current_compute_name)
    if num_replicas:
        json_payload['numReplicas'] = num_replicas
    else:
        del(json_payload['numReplicas'])
    if enable_model_data_collection and disable_model_data_collection:
        raise CLIError('Please provide only one flag to enable or disable model data collection')
    elif enable_model_data_collection:
        json_payload['dataCollection']['storageEnabled'] = True
    elif disable_model_data_collection:
        json_payload['dataCollection']['storageEnabled'] = False
    else:
        del(json_payload['dataCollection'])

    if not image_id:
        result, service_payload = _mms_service_show(service_id, verb, context)
        try:
            image_id = service_payload['Image']['Id']
        except KeyError:
            raise CLIError('Unable to retrieve image id from service details')
    json_payload['imageId'] = image_id

    try:
        resp = context.http_call('put', service_url, params=params, headers=headers, json=json_payload, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise CLIError('Error connecting to {}.'.format(service_url))
    except requests.Timeout:
        raise CLIError('Error, request to {} timed out.'.format(service_url))

    if resp.status_code != 202:
        raise CLIError('Error occurred updating service {}.\nStatus Code: {}\nHeaders: {}\nContent: {}'.format(service_id, resp.status_code, resp.headers, resp.content))

    try:
        operation_location = resp.headers['Operation-Location']
    except KeyError:
        raise CLIError('Invalid response header key: Operation-Location')
    create_operation_status_id = operation_location.split('/')[-1]

    if verb:
        print("Operation Id: {}".format(create_operation_status_id))

    operation_url = get_current_model_management_url_base() + MMS_OPERATION_URL_ENDPOINT.format(create_operation_status_id)
    operation_headers = {'Authorization': auth_header}

    sys.stdout.write('Updating service')
    sys.stdout.flush()
    service_id = poll_mms_async_operation(operation_url, operation_headers, params,
                                          MMS_SERVICE_CREATE_OPERATION_POLLING_MAX_TRIES, context)
    print('Done')
    print('Service ID: {}'.format(service_id))
    return SUCCESS_RETURN_CODE
