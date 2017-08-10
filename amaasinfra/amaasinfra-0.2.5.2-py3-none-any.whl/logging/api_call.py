""" Logs calls to the AMaaS APIs """

from datetime import datetime

import boto3

class APICallLogger(object):
    """ The current implementation of the API Call Logger uses Cloudwatch metrics """

    def __init__(self):
        self.client = boto3.client('cloudwatch')

    def record_api_call(self, asset_manager_id, api_call_type, api_call_subtype, environment='dev'):
        """ Record the API call """
        asset_manager_id = str(asset_manager_id)  # In case it gets sent in as an integer
        self.client.put_metric_data(
            Namespace='amaas',
            MetricData=[
                {
                    'MetricName': 'AMaaSAPICalls',
                    'Dimensions': [
                        {'Name': 'api_call_type', 'Value': api_call_type},
                        {'Name': 'api_call_subtype', 'Value': api_call_subtype},
                        {'Name': 'asset_manager_id', 'Value': asset_manager_id},
                        {'Name': 'environment', 'Value': environment}
                    ],
                    'Timestamp': datetime.utcnow(),
                    'Value': 1,
                    'Unit': 'Count'
                },
            ]
        )
