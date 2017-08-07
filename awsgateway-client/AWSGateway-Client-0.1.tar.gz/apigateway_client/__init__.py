from awsrequests import AwsRequester
import requests
import boto3


class Client():
    def __init__(self, api_gateway_id, region, stage, endpoint_key,
                 account_id=None, role=None, role_session_name=None, api_key=None):
        '''
        '''
        self.api_gateway_id = api_gateway_id
        self.region = region
        self.stage = stage
        self.endpoint_key = endpoint_key
        self.account_id = account_id
        self.role = role
        self.role_session_name = role_session_name
        self.assume = None
        if self.role:
            self.role_arn = self.__set_role_arn()
        self.api_key = api_key

    def __build_url(self, endpoint_meta=None):
        '''
        Build apigateway URL based on arguments provided
        '''
        if not endpoint_meta:
            return "https://{api_gateway_id}.execute-api.{region}.amazonaws.com/{stage}/{endpoint_key}".format(
                api_gateway_id=self.api_gateway_id,
                region=self.region,
                stage=self.stage,
                endpoint_key=self.endpoint_key
                )
        return "https://{api_gateway_id}.execute-api.{region}.amazonaws.com/{stage}/{endpoint_key}/{endpoint_meta}".format(
            api_gateway_id=self.api_gateway_id,
            region=self.region,
            stage=self.stage,
            endpoint_key=self.endpoint_key,
            endpoint_meta=endpoint_meta
            )


    def __set_temp_creds(self, assume=None):
        if not assume:
            assume = self.assume
        _temp_creds = dict(
            aws_access_key_id=assume['Credentials']['AccessKeyId'],
            aws_secret_access_key=assume['Credentials']['SecretAccessKey'],
            aws_session_token=assume['Credentials']['SessionToken']
            )

        return _temp_creds

    def __set_role_arn(self):
        return "arn:aws:iam::{account_id}:role/{role}".format(
            account_id=self.account_id,
            role=self.role
            )

    def __create_client(self):
        return boto3.client('sts')

    def __assume_role(self):
        sts = self.__create_client()
        assume = sts.assume_role(
            RoleArn=self.__set_role_arn(),
            RoleSessionName=self.role_session_name
            )
        return self.__set_temp_creds(assume)

    def get(self, region='us-east-1', endpoint_meta=None):
        if not self.api_key:
            temp_creds = self.__assume_role()
            api_gateway = AwsRequester(
                region,
                *(temp_creds[key] for key in ['aws_access_key_id',
                                              'aws_secret_access_key', 'aws_session_token'])
                )
            if endpoint_meta:
                return api_gateway.get(self.__build_url(endpoint_meta))
            return api_gateway.get(self.__build_url())
        else:
            headers = {"content-type": "application/json","x-api-key": self.api_key}
            if endpoint_meta:
                return requests.get(self.__build_url(endpoint_meta), headers=headers)
            return requests.get(self.__build_url(), headers=headers)
