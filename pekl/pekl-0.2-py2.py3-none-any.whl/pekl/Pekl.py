import boto3
import json
import os
import sys
import time
from datetime import datetime
import uuid

class Pekl(object):

    def __init__(self, bucket_name, region_name=None):
        self.bucket_name = bucket_name
        if region_name is not None:
            self.region = region_name
        else:
            # Check to see if the AWS_REGION environment variable has been set
            self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.aws_lambda = boto3.client("lambda", region_name=self.region)
        self.s3 = boto3.client("s3", region_name=self.region)
        return None


    def receive(self, event):
        if "pekl_bucket_name" in event and "pekl_bucket_key" in event:
            # a file has been passed through from the Pekl library, we need
            # to collect it from S3
            bucket_response = self.s3.get_object(
                Bucket=event.get("pekl_bucket_name"),
                Key=event.get("pekl_bucket_key")
            )
            try:
                event = bucket_response.get("Body").read()
                event = json.loads(event)
            except Exception as exception:
                # We are going to need much better exception handling in this
                print "bugger"
                return {
                    "error" : str(exception)
                }
        return event


    def respond(self, event):
        json_string = json.dumps(event)
        size = sys.getsizeof(json_string)
        if size > 5000000:
            # This response risks being too big to respond with so we need to
            # transfer it via the bucket
            random_key = self.writeToBucket(json_string)

            return json.dumps({
                "pekl_bucket_name" : self.bucket_name,
                "pekl_bucket_key" : random_key
            })
        # if it's not larger than 5 fake MB then we should be returning the
        # json string
        return json_string


    def invoke(self, function_name, body, region_name=None):
        json_string = json.dumps(body)
        size = sys.getsizeof(json_string)
        if size > 5000000:
            random_key = self.writeToBucket(json_string)
            json_string = json.dumps({
                "pekl_bucket_name" : self.bucket_name,
                "pekl_bucket_key" : random_key
            })
        response = self.aws_lambda.invoke(
            FunctionName = function_name,
            InvocationType = "RequestResponse",
            Payload = json_string
        )
        response_body = respone.get("Payload").read()
        return_dict = self.receive(response_body)
        return return_dict


    def invokeAsync(self, function_name, body, region_name):
        json_string = json.dumps(body)
        size = sys.getsizeof(json_string)
        if size > 5000000:
            random_key = self.writeToBucket(json_string)
            json_string = json.dumps({
                "pekl_bucket_name" : self.bucket_name,
                "pekl_bucket_key" : random_key
            })
        self.aws_lambda.invoke(
            FunctionName = function_name,
            InvocationType = "Event",
            Payload = json_string
        )
        return None


    def writeToBucket(self, json_string):
        # Creating a random string that's based on milisecond time so
        # that it's incredibly, incredibly unlikely to have a duplicate
        # key
        random_key = str(datetime.utcnow()).replace(" ", "") + str(uuid.uuid4()) + ".txt"

        self.s3.put_object(
            ACL="private",
            Bucket=self.bucket_name,
            Key=random_key,
            Body=json_string
        )
        return random_key
