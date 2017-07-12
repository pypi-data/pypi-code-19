import boto3

def client():
    return boto3.client('ec2')

def resource():
    return boto3.resource('ec2')