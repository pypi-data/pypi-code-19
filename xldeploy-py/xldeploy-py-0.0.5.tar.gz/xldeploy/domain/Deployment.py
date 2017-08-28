import json


class Deployment(object):

    @staticmethod
    def as_deployment(json):
        required_deployments = None
        deployment_group_index = None
        if 'requiredDeployments' in json:
            required_deployments = json['requiredDeployments']
        if 'deploymentGroupIndex' in json:
            deployment_group_index = json['deploymentGroupIndex']
        deployment = Deployment(json['id'], json['application'], json['deployeds'], json['deployables'],
                                json['containers'], required_deployments, deployment_group_index,
                                json['type'])
        return deployment

    def __init__(self, id, application, deployeds, deployables, containers, requiredDeployments,
                 deploymentGroupIndex, type):
        self.id = id
        self.application = application
        self.deployeds = deployeds
        self.deployables = deployables
        self.containers = containers
        self.requiredDeployments = requiredDeployments
        self.deploymentGroupIndex = deploymentGroupIndex
        self.type = type

    def to_dict(self):
        return dict(id=self.id, application=self.application, deployeds=self.deployeds, deployables=self.deployables,
                    containers=self.containers, requiredDeployments=self.requiredDeployments,
                    deploymentGroupIndex=self.deploymentGroupIndex, type=self.type)

