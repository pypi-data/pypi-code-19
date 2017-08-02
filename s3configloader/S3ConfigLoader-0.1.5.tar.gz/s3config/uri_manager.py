# **********************************
# currently supported set of uri are
# S3 - s://buckey/key
# file -  file://path
# **********************************

import boto3


class UnsupportedURIException(Exception):
    pass


def get_s3_resource(resource):
    tokens = resource.split("/")
    bucket = tokens[0]
    key = "/".join(tokens[1:])
    client = boto3.client('s3')
    return client.get_object(Bucket=bucket,
                             Key=key)['Body'].read()


def get_file_resource(resource):
    f = open(resource, "r")
    return f.read()


def get_resource_data_from_uri(uri):
    tokens = uri.split("://")
    protocol = tokens[0]
    resource = tokens[1]
    if protocol == "s3":
        return get_s3_resource(resource)
    elif protocol == "file":
        return get_file_resource(resource)
    else:
        raise UnsupportedURIException("The only supported URI types are s3:// and file://. Please use one of these")
