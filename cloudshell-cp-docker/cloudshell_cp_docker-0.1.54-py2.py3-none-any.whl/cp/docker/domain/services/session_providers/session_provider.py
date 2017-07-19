from cloudshell.cp.docker.models.clients import Clients
from docker import APIClient, DockerClient
from docker.tls import TLSConfig


class SessionProvider(object):
    def __init__(self):
        return

    def get_clients(self, cloudshell_session, docker_resource_model):
        """
        :param cloudshell.api.cloudshell_api.CloudShellAPISession cloudshell_session:
        :param docker_resource_model:
        :return:
        :rtype: Clients
        """
        api_client = self._get_api_client(cloudshell_session=cloudshell_session,
                                          docker_resource_model=docker_resource_model)

        docker_client = self._get_docker_client(cloudshell_session=cloudshell_session,
                                                docker_resource_model=docker_resource_model)

        return Clients(api_client=api_client,
                       docker_client=docker_client)

    def _get_docker_client(self, cloudshell_session, docker_resource_model):
        tls_config = TLSConfig(ca_cert='C:\Docker\Certs\ca.pem',
                               client_cert=('C:\Docker\Certs\cert.pem', 'C:\Docker\Certs\key.pem'),
                               verify=True)

        docker_client = DockerClient(base_url='tcp://192.168.0.252:2376',
                                     timeout=10,
                                     tls=tls_config,
                                     user_agent='Quali CloudShell',
                                     version='auto')

        docker_client.ping()

        return docker_client

    def _get_api_client(self, cloudshell_session, docker_resource_model):
        tls_config = TLSConfig(ca_cert='C:\Docker\Certs\ca.pem',
                               client_cert=('C:\Docker\Certs\cert.pem', 'C:\Docker\Certs\key.pem'),
                               verify=True)

        api_client = APIClient(base_url='tcp://192.168.0.252:2376',
                               timeout=10,
                               tls=tls_config,
                               user_agent='Quali CloudShell',
                               version='auto')

        api_client.ping()

        return api_client
