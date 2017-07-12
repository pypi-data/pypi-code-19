import boto3


def client():
    """
    A low-level client representing Amazon Simple Systems Manager (SSM)
    
    :return: a connection 
    :rtype: botocore.client.SSM
    """
    return boto3.client('ssm')
