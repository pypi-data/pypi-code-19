from AwsProcessor import AwsProcessor
from stdplusAwsHelpers.AwsConnectionFactory import AwsConnectionFactory

from pprint import pprint

class AwsRole(AwsProcessor):
    def __init__(self,stackResource,parent):
        """Construct an AwsRole command processor"""
        AwsProcessor.__init__(self,parent.raw_prompt + "/role:" + stackResource.logical_id,parent)
        self.stackResource = stackResource
        self.do_refresh('')

    def do_refresh(self,args):
        """Refresh the view of the log group"""
        print "stackResource: {}".format(self.stackResource)
        
        self.roleDetails = AwsConnectionFactory.getIamClient().get_role(RoleName=self.stackResource.physical_resource_id)
        print "== role details =="
        pprint(self.roleDetails)

        self.rolePolicies = self.loadRolePolicies()
        print "== attached policies =="
        pprint(self.rolePolicies)
        

    def loadRolePolicies(self):
        response = AwsConnectionFactory.getIamClient().list_role_policies(RoleName=self.stackResource.physical_resource_id)

        rolePolicyNames = response['PolicyNames']
        result = {}
        for policyName in rolePolicyNames:
            result[policyName] = AwsConnectionFactory.getIamClient().get_role_policy(RoleName=self.stackResource.physical_resource_id,PolicyName=policyName)

        return result

