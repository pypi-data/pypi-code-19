import boto3
import json

from troposphere import Base64, FindInMap, GetAtt, Join, Output
from troposphere import Parameter, Ref, Tags, Template
from troposphere.rds import DBInstance, DBSubnetGroup, DBParameterGroup
from troposphere.autoscaling import Metadata
from troposphere.ec2 import PortRange, NetworkAcl, NatGateway, Route, \
    VPCGatewayAttachment, SubnetRouteTableAssociation, Subnet, RouteTable, \
    VPC, NetworkInterfaceProperty, NetworkAclEntry, \
    SubnetNetworkAclAssociation, EIP, Instance, InternetGateway, \
    SecurityGroupRule, SecurityGroup
from troposphere.policies import CreationPolicy, ResourceSignal
from troposphere.cloudformation import Init, InitFile, InitFiles, InitConfig, \
    InitService, InitServices


class CloudFormationTemplate(object):
    """
    This class is for generating CloudFormation templates in different ways
    """
    @staticmethod
    def generate_basic_template():
        """
        This method is to create basic AWS infra layer that AMaaS requires
        """
        t = Template()
        t.add_description("""Basic template for AMaaS
        cloud infrastructure on AWS""")
        t.add_version('2010-09-09')

        ref_stack_id = Ref('AWS::StackId')
        ref_region = Ref('AWS::Region')
        ref_stack_name = Ref('AWS::StackName')

        # setup VPC and subnets, basically all the networking stuff
        vpc = t.add_resource(VPC('VPC',
                                 CidrBlock='10.0.0.0/16',
                                 Tags=Tags(Application=ref_stack_id)))

        # add access control here
        acl = t.add_resource(NetworkAcl('NetworkACL',
                                        VpcId=Ref(vpc),
                                        Tags=Tags(Application=ref_stack_id)))

        igw = t.add_resource(
            InternetGateway('InternetGateway',
                            Tags=Tags(Application=ref_stack_id)))

        # add internet gateway and route table
        igw_attachment = t.add_resource(
            VPCGatewayAttachment('AttachGateway',
                                 VpcId=Ref(vpc),
                                 InternetGatewayId=Ref(igw)))

        nat_rt_tbl = t.add_resource(
            RouteTable('NAT',
                       VpcId=Ref(vpc),
                       Tags=Tags(Application=ref_stack_id)))

        public_rt_tbl = t.add_resource(
            RouteTable('Public',
                       VpcId=Ref(vpc),
                       Tags=Tags(Application=ref_stack_id)))

        private_subnet1 = t.add_resource(
            Subnet('PrivateSubnet1',
                   CidrBlock='10.0.1.0/24',
                   AvailabilityZone='ap-southeast-1a',
                   VpcId=Ref(vpc),
                   Tags=Tags(Application=ref_stack_id)))

        private_subnet2 = t.add_resource(
            Subnet('PrivateSubnet2',
                   CidrBlock='10.0.2.0/24',
                   AvailabilityZone='ap-southeast-1b',
                   VpcId=Ref(vpc),
                   Tags=Tags(Application=ref_stack_id)))

        public_subnet1 = t.add_resource(
            Subnet('PublicSubnet1',
                   CidrBlock='10.0.3.0/24',
                   AvailabilityZone='ap-southeast-1a',
                   VpcId=Ref(vpc),
                   Tags=Tags(Application=ref_stack_id)))

        public_subnet2 = t.add_resource(
            Subnet('PublicSubnet2',
                   CidrBlock='10.0.4.0/24',
                   AvailabilityZone='ap-southeast-1b',
                   VpcId=Ref(vpc),
                   Tags=Tags(Application=ref_stack_id)))

        nat_eip = t.add_resource(EIP('NatEip', Domain="vpc"))

        nat = t.add_resource(NatGateway('Nat',
                                        AllocationId=GetAtt(nat_eip,
                                                            'AllocationId'),
                                        SubnetId=Ref(public_subnet1)))

        t.add_resource(Route('NatRoute',
                             RouteTableId=Ref(nat_rt_tbl),
                             DestinationCidrBlock='0.0.0.0/0',
                             NatGatewayId=Ref(nat)))

        t.add_output(Output('VPCId',
                            Value=Ref(vpc),
                            Description='VPC Id'))

        t.add_output(Output('NatEip',
                            Value=Ref(nat_eip),
                            Description='Nat Elastic IP'))

        # associate the subnets to Network ACL
        private_subnet1_association = t.add_resource(
            SubnetNetworkAclAssociation('PrivateSubnet1ACL',
                                        SubnetId=Ref(private_subnet1),
                                        NetworkAclId=Ref(acl)))

        private_subnet2_association = t.add_resource(
            SubnetNetworkAclAssociation('PrivateSubnet2ACL',
                                        SubnetId=Ref(private_subnet2),
                                        NetworkAclId=Ref(acl)))

        public_subnet1_association = t.add_resource(
            SubnetNetworkAclAssociation('PublicSubnet1ACL',
                                        SubnetId=Ref(public_subnet1),
                                        NetworkAclId=Ref(acl)))

        public_subnet2_association = t.add_resource(
            SubnetNetworkAclAssociation('PublicSubnet2ACL',
                                        SubnetId=Ref(public_subnet2),
                                        NetworkAclId=Ref(acl)))

        # associate the subnets to route table
        private_subnet1_association = t.add_resource(
            SubnetRouteTableAssociation('PrivateSubnet1Association',
                                        SubnetId=Ref(private_subnet1),
                                        RouteTableId=Ref(nat_rt_tbl)))

        private_subnet2_association = t.add_resource(
            SubnetRouteTableAssociation('PrivateSubnet2Association',
                                        SubnetId=Ref(private_subnet2),
                                        RouteTableId=Ref(nat_rt_tbl)))

        public_subnet1_association = t.add_resource(
            SubnetRouteTableAssociation('PublicSubnet1Association',
                                        SubnetId=Ref(public_subnet1),
                                        RouteTableId=Ref(public_rt_tbl)))

        public_subnet2_association = t.add_resource(
            SubnetRouteTableAssociation('PublicSubnet2Association',
                                        SubnetId=Ref(public_subnet2),
                                        RouteTableId=Ref(public_rt_tbl)))
        # add the route rules
        route = t.add_resource(Route('PublicRoute',
                                     DependsOn='AttachGateway',
                                     GatewayId=Ref('InternetGateway'),
                                     DestinationCidrBlock='0.0.0.0/0',
                                     RouteTableId=Ref(public_rt_tbl)))

        return t
        

class CloudFormationManager(object):
    """
    This is a class to manage CloudFormation tasks programmatically
    """
    def __init__(self):
        self.cf = boto3.client('cloudformation')

    def create_default_stack(self):
        """
        This method is used to create default AMaaS infra stack
        :return:
        """
        return self.cf.create_stack(StackName='Default',
                                    TemplateBody=CloudFormationTemplate.
                                    generate_basic_template().to_json())

    def create_stack(self, starck_name, template):
        """
        This method is used to create a new CloudFormation stack
        """
        return self.cf.create_stack(StackName=starck_name,
                                    TemplateBody=template)

    def delete_stack(self, stack_name):
        """
        This method is used to delete a named CloudFormation stack
        """
        return self.cf.delete_stack(StackName=stack_name)


