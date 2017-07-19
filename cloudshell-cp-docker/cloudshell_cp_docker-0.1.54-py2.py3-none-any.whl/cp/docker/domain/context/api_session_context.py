class ApiSessionContext(object):
    def __init__(self, cloudshell_session, docker_resource_model, docker_session_manager):
        """
        Initializes an instance of DockerApiSessionContext
        :param cloudshell_session:
        :param docker_resource_model:
        :param docker_session_manager:

        """
        self.cloudshell_session = cloudshell_session
        self.docker_resource_model = docker_resource_model
        self.docker_session_manager = docker_session_manager

    def __enter__(self):
        """
        Initializes all available docker api clients and sessions
        :rtype: DockerApiClients
        """
        return self.docker_session_manager.get_clients(cloudshell_session=self.cloudshell_session, docker_resource_model=self.docker_resource_model)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called upon end of the context. Does nothing
        :param exc_type: Exception type
        :param exc_val: Exception value
        :param exc_tb: Exception traceback
        :return:
        """
        return
