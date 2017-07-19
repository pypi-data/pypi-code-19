from cloudshell.shell.core.context import ResourceCommandContext


class ResourceModelContext(object):
    def __init__(self, context, model_parser):
        """
        Initializes an instance of DockerResourceModelContext
        :param ResourceCommandContext context: Command context
        :param DockerModelsParser model_parser:
        """
        self.context = context
        self.model_parser = model_parser

    def __enter__(self):
        """
        Initializes DockerResourceModelContext instance from a context
        :rtype: DockerCloudProviderResourceModel
        :return :
        """
        return self.model_parser.convert_to_docker_resource_model(self.context.resource)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called upon end of the context. Does nothing
        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return:
        """
        pass
