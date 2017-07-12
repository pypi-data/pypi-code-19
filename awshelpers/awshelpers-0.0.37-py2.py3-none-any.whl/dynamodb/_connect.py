import boto3

def client():
    return boto3.client('dynamodb')

def resource():
    return boto3.resource('dynamodb')