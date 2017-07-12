from awshelpers.s3 import _connect


def item(bucket, key, destination):
    """
    Download S3 object
    
    :param bucket: name of root S3 bucket
    :type bucket: str
    :param key: name (path) to object within root S3 bucket
    :type key: str
    :param destination: where to download object to locally 
    :type destination: str
    :return: None
    :rtype: None
    """
    return _connect.resource().Bucket(bucket).download_file(key, destination)
