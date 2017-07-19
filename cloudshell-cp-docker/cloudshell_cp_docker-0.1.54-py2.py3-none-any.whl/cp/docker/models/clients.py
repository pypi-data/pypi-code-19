class Clients(object):
    def __init__(self, api_client, docker_client):
        self.api_client = api_client
        self.docker_client = docker_client
