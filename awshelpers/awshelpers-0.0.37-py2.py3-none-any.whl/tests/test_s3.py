from awshelpers.s3 import get as s3_get


def test():
    """
    Download a known object from S3
    
    :return: None if successful
    :rtype: None
    """
    assert s3_get.item('lasso-ops', 'summon/ops/summon.yml', '/tmp/summon.yml') is None
