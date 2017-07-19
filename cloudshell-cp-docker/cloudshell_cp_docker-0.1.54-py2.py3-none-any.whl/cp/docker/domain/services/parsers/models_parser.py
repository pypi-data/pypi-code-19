import jsonpickle

from cloudshell.cp.docker.common.deploy_data_holder import DeployDataHolder
from cloudshell.cp.docker.models.deploy_docker_container_resource_model import DeployDockerContainerResourceModel
from cloudshell.cp.docker.models.cloud_provider_resource_model import CloudProviderResourceModel


class ModelsParser(object):
    @staticmethod
    def convert_app_resource_to_deployed_app(resource):
        json_str = jsonpickle.decode(resource.app_context.deployed_app_json)
        data_holder = DeployDataHolder(json_str)

        return data_holder

    @staticmethod
    def convert_to_docker_resource_model(resource):
        resource_context = resource.attributes

        docker_resource_model = CloudProviderResourceModel()

        return docker_resource_model

    @staticmethod
    def convert_to_deployment_resource_model(deployment_request):
        data = jsonpickle.decode(deployment_request)

        data_holder = DeployDataHolder(data)

        deployment_resource_model = DeployDockerContainerResourceModel()
        deployment_resource_model.app_name = data_holder.app_name
        deployment_resource_model.cloud_provider = data_holder.docker_params.cloud_provider
        deployment_resource_model.docker_container_command = data_holder.docker_params.docker_container_command
        deployment_resource_model.docker_image = data_holder.docker_params.docker_image
        deployment_resource_model.docker_image_shell = data_holder.docker_params.docker_image_shell
        deployment_resource_model.docker_image_tag = data_holder.docker_params.docker_image_tag

        return deployment_resource_model

    @staticmethod
    def convert_to_bool(string):
        """
        Converts string to bool
        :param string: String
        :str string: str
        :return: True or False
        """
        if isinstance(string, bool):
            return string
        return string in ['true', 'True', '1']

    @staticmethod
    def get_public_ip_from_connected_resource_details(resource_context):
        public_ip_on_resource = ""
        public_ip = 'Public IP'
        if resource_context.remote_endpoints is not None and public_ip in resource_context.remote_endpoints[
            0].attributes:
            public_ip_on_resource = resource_context.remote_endpoints[0].attributes[public_ip]
        return public_ip_on_resource

    @staticmethod
    def get_private_ip_from_connected_resource_details(resource_context):
        private_ip_on_resource = ""
        if resource_context.remote_endpoints is not None:
            private_ip_on_resource = resource_context.remote_endpoints[0].address
        return private_ip_on_resource

    @staticmethod
    def try_get_deployed_connected_resource_instance_id(resource_context):
        try:
            deployed_instance_id = str(
                jsonpickle.decode(resource_context.remote_endpoints[0].app_context.deployed_app_json)['vmdetails'][
                    'uid'])
        except Exception as e:
            raise ValueError('Could not find an ID of the Docker Deployed instance' + e.message)
        return deployed_instance_id

    @staticmethod
    def get_connectd_resource_fullname(resource_context):
        if resource_context.remote_endpoints[0]:
            return resource_context.remote_endpoints[0].fullname
        else:
            raise ValueError('Could not find resource fullname on the deployed app.')
