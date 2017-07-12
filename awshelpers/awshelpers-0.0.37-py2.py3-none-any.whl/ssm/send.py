from awshelpers.ssm import _connect


def command(instance_ids, document_name, timeout, comment, commands, s3_region, s3_bucket, s3_prefix):
    """
    Sends command to SSM
    
    :param instance_ids: single or multiple instance ids
    :type instance_ids: list
    
    :param document_name: custom or existing SSM document name
    :type document_name: str
    
    :param timeout: time in seconds
    :type timeout: int
    
    :param comment: comment for command
    :type comment: str
    
    :param commands: command to be run
    :type commands: list
    
    :param s3_region: region of S3 bucket to store command output
    :type s3_region: str
    
    :param s3_bucket: name of S3 bucket to store command output
    :type s3_bucket: str
    
    :param s3_prefix: representation of path in S3 bucket
    :type s3_prefix: str
    
    :return: dict
    """
    return _connect.client().send_command(
        InstanceIds=instance_ids,
        DocumentName=document_name,
        TimeoutSeconds=timeout,
        Comment=comment,
        Parameters={
            'commands': commands
        },
        OutputS3Region=s3_region,
        OutputS3BucketName=s3_bucket,
        OutputS3KeyPrefix=s3_prefix,
    )
