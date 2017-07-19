import jsonpickle

from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.cp.docker.common.deploy_data_holder import DeployDataHolder
from cloudshell.cp.docker.domain.context.shell_context import ShellContext
from cloudshell.cp.docker.domain.services.parsers.command_results_parser import CommandResultsParser
from cloudshell.cp.docker.domain.services.parsers.models_parser import ModelsParser
from cloudshell.cp.docker.domain.services.session_providers.session_provider import SessionProvider
from cloudshell.cp.docker.models.deploy_result import DeployResult
from cloudshell.cp.docker.models.prepare_connectivity_action_result import PrepareConnectivityActionResult
from docker.errors import APIError, ImageNotFound, NotFound


class DockerShell:
    def __init__(self):
        self.command_result_parser = CommandResultsParser()
        self.docker_session_manager = SessionProvider()
        self.model_parser = ModelsParser()

        return

    def get_inventory(self, context):
        return

    def container_create(self, command_context, deployment_request, cancellation_context, something_else):
        with ShellContext(context=command_context, docker_session_manager=self.docker_session_manager) as shell_context:
            with ErrorHandlingContext(shell_context.logger):
                shell_context.logger.info('Deploying Container')

                reservation_id = command_context.reservation.reservation_id[-12:]

                shell_context.logger.debug('deployment_request: %s' % deployment_request)
                docker_container_deployment_model = self.model_parser.convert_to_deployment_resource_model(deployment_request)

                container_name = "cs_%s.%s" % (reservation_id, docker_container_deployment_model.app_name)
                container_create_args = {'detach': True, 'name': container_name}

                image = docker_container_deployment_model.docker_image
                if docker_container_deployment_model.docker_image_tag:
                    image += ":%s" % docker_container_deployment_model.docker_image_tag
                container_create_args['image'] = image

                command = docker_container_deployment_model.docker_container_command
                if command:
                    container_create_args['command'] = command

                shell_context.logger.debug('Container Create Args: %s' % container_create_args)
                try:
                    shell_context.clients.docker_client.images.pull(name=docker_container_deployment_model.docker_image,
                                                                    tag=docker_container_deployment_model.docker_image_tag)
                    container = shell_context.clients.docker_client.containers.create(**container_create_args)
                except Exception as e:
                    shell_context.logger.error("Unhandled Exception '%s' - '%s'" % (type(e).__name__, e.message))
                    raise e
                shell_context.logger.debug('Container Created')

                deployed_app_attributes = {}
                # deployed_app_attributes = {
                #     'Docker Container Command': docker_container_deployment_model.docker_container_command,
                #     'Docker Image': docker_container_deployment_model.docker_image,
                #     'Docker Image Tag': docker_container_deployment_model.docker_image_tag,
                #     'Docker Image Shell': docker_container_deployment_model.docker_image_shell,
                #     'Password': command_context.resource.attributes['Password'],
                #     'User': command_context.resource.attributes['User']
                # }

                deploy_result = DeployResult(vm_name=docker_container_deployment_model.app_name,
                                             vm_uuid=container.id,
                                             cloud_provider_resource_name=docker_container_deployment_model.cloud_provider,
                                             auto_power_off=True,
                                             wait_for_ip=False,
                                             auto_delete=True,
                                             autoload=False,
                                             deployed_app_attributes=deployed_app_attributes,
                                             deployed_app_address=command_context.resource.address)

                shell_context.logger.debug('Returning deploy_result: %s' % deploy_result)
                return deploy_result

    def container_inspect(self, command_context):
        with ShellContext(context=command_context, docker_session_manager=self.docker_session_manager) as shell_context:
            with ErrorHandlingContext(shell_context.logger):
                resource = command_context.remote_endpoints[0]
                data_holder = self.model_parser.convert_app_resource_to_deployed_app(resource)

                shell_context.logger.info('Inspecting Container - %s' % data_holder.vmdetails.uid)

                output = None
                try:
                    output = shell_context.clients.api_client.inspect_container(container=data_holder.vmdetails.uid)
                except NotFound as e:
                    shell_context.logger.warn("Attempting to inspect container '%s' which does not exist!" % data_holder.vmdetails.uid)
                except Exception as e:
                    shell_context.logger.error("Unhandled Exception '%s' - '%s'" % (type(e).__name__, e.message))
                    raise e

        return output

    def container_logs(self, command_context):
        with ShellContext(context=command_context, docker_session_manager=self.docker_session_manager) as shell_context:
            with ErrorHandlingContext(shell_context.logger):
                resource = command_context.remote_endpoints[0]
                data_holder = self.model_parser.convert_app_resource_to_deployed_app(resource)

                shell_context.logger.info('Retrieving Logs for Container - %s' % data_holder.vmdetails.uid)

                output = None
                try:
                    container = shell_context.clients.docker_client.containers.get(container_id=data_holder.vmdetails.uid)
                    output = container.logs()
                except NotFound as e:
                    shell_context.logger.warn("Attempting to retrieve logs for container '%s' which does not exist!" % data_holder.vmdetails.uid)
                except Exception as e:
                    shell_context.logger.error("Unhandled Exception '%s' - '%s'" % (type(e).__name__, e.message))
                    raise e

        return output

    def container_rm(self, command_context):
        with ShellContext(context=command_context, docker_session_manager=self.docker_session_manager) as shell_context:
            with ErrorHandlingContext(shell_context.logger):
                resource = command_context.remote_endpoints[0]
                data_holder = self.model_parser.convert_app_resource_to_deployed_app(resource)

                shell_context.logger.info('Removing Container - %s' % data_holder.vmdetails.uid)
                try:
                    container = shell_context.clients.docker_client.containers.get(container_id=data_holder.vmdetails.uid)
                    container.remove(force=True)
                except NotFound as e:
                    shell_context.logger.warn("Attempting to remove container '%s' which does not exist!" % data_holder.vmdetails.uid)
                except Exception as e:
                    shell_context.logger.error("Unhandled Exception '%s' - '%s'" % (type(e).__name__, e.message))
                    raise e

        return True

    def power_off(self, command_context):
        with ShellContext(context=command_context, docker_session_manager=self.docker_session_manager) as shell_context:
            with ErrorHandlingContext(shell_context.logger):
                shell_context.logger.info('Power Off')

                resource = command_context.remote_endpoints[0]
                data_holder = self.model_parser.convert_app_resource_to_deployed_app(resource)

                try:
                    container = shell_context.clients.docker_client.containers.get(container_id=data_holder.vmdetails.uid)
                    container.stop()
                except NotFound as e:
                    shell_context.logger.warn("Attempting to stop container '%s' which does not exist!" % data_holder.vmdetails.uid)
                except Exception as e:
                    shell_context.logger.error("Unhandled Exception '%s' - '%s'" % (type(e).__name__, e.message))
                    raise e

                shell_context.cloudshell_session.SetResourceLiveStatus(resource.fullname, "Offline", "Powered Off")

    def power_on(self, command_context):
        with ShellContext(context=command_context, docker_session_manager=self.docker_session_manager) as shell_context:
            with ErrorHandlingContext(shell_context.logger):
                shell_context.logger.info('Power On')

                resource = command_context.remote_endpoints[0]
                data_holder = self.model_parser.convert_app_resource_to_deployed_app(resource)

                try:
                    container = shell_context.clients.docker_client.containers.get(container_id=data_holder.vmdetails.uid)
                    container.start()
                except NotFound as e:
                    shell_context.logger.warn("Attempting to start container '%s' which does not exist!" % data_holder.vmdetails.uid)
                    shell_context.cloudshell_session.SetResourceLiveStatus(resource.fullname, "Offline", "Powered Off")
                except Exception as e:
                    shell_context.logger.error("Unhandled Exception '%s' - '%s'" % (type(e).__name__, e.message))
                    shell_context.cloudshell_session.SetResourceLiveStatus(resource.fullname, "Offline", "Powered Off")
                    raise e

                shell_context.cloudshell_session.SetResourceLiveStatus(resource.fullname, "Online", "Active")

    def prepare_connectivity(self, command_context, request, cancellation_context):
        with ShellContext(context=command_context, docker_session_manager=self.docker_session_manager) as shell_context:
            with ErrorHandlingContext(shell_context.logger):
                shell_context.logger.info('Prepare Connectivity')

                decoded_request = DeployDataHolder(jsonpickle.decode(request))
                prepare_connectivity_request = None
                if hasattr(decoded_request, 'driverRequest'):
                    prepare_connectivity_request = decoded_request.driverRequest
                if not prepare_connectivity_request:
                    raise ValueError('Invalid prepare connectivity request')

                results = []

                result = PrepareConnectivityActionResult()
                result.infoMessage = 'PrepareConnectivity finished successfully'

                results.append(result)

                return self.command_result_parser.set_command_result({'driverResponse': {'actionResults': results}})
        return
