import boto3
import json


class Pekl(object):

    def __init__(self, bucket_name, region_name=None):
        self.bucket_name = bucket_name
        if region_name is not None:
            self.region = region_name
        else:
            self.region = "us-east-1"
        self.aws_lambda = boto3.client("lambda", region_name=self.region)
        self.s3 = boto3.client("s3", region_name=self.region)
        return self


    def receive(self, event):
        return event


    def respond(self, event):
        return event


    def invoke(self, function_name, body, region_name=None):
        return body


    def invokeAsync(self, function_name, body, region_name):
        return None
