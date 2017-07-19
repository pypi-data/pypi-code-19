from cloudshell.core.context.error_handling_context import ErrorHandlingContext
from cloudshell.cp.docker.domain.context.api_session_context import ApiSessionContext
from cloudshell.cp.docker.domain.context.resource_model_context import ResourceModelContext
from cloudshell.cp.docker.domain.services.parsers.models_parser import ModelsParser
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext


class ShellContext(object):
    def __init__(self, context, docker_session_manager):
        """
        Initializes an instance of DockerShellContext
        :param ResourceCommandContext context: Command context
        """
        self.context = context
        self.docker_session_manager = docker_session_manager
        self.model_parser = ModelsParser()

    def __enter__(self):
        """
        Initializes all docker shell context dependencies
        :rtype DockerShellContextModel:
        """
        with LoggingSessionContext(self.context) as logger:
            with ErrorHandlingContext(logger):
                with CloudShellSessionContext(self.context) as cloudshell_session:
                    with ResourceModelContext(self.context, self.model_parser) as docker_resource_model:
                        with ApiSessionContext(docker_session_manager=self.docker_session_manager,
                                               cloudshell_session=cloudshell_session,
                                               docker_resource_model=docker_resource_model) as clients:
                            return ShellContextModel(logger=logger,
                                                     cloudshell_session=cloudshell_session,
                                                     docker_resource_model=docker_resource_model,
                                                     clients=clients)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called upon end of the context. Does nothing
        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return:
        """
        return


class ShellContextModel(object):
    def __init__(self, logger, cloudshell_session, docker_resource_model, clients):
        """
        :param logging.Logger logger:
        :param cloudshell.api.cloudshell_api.CloudShellAPISession cloudshell_session:
        :param docker_resource_model:
        :param clients:
        :return:
        """
        self.logger = logger
        self.cloudshell_session = cloudshell_session
        self.docker_resource_model = docker_resource_model
        self.clients = clients
