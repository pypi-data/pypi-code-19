import boto3

def client():
    return boto3.client('s3')

def resource():
    return boto3.resource('s3')