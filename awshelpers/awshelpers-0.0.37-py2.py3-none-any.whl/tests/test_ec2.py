from awshelpers.ec2 import describe as ec2_describe

AWSHELPERS_NETWORK_INTERFACE = 'eni-3b630110'
AWSHELPERS_INSTANCE_ID = 'i-073a59252f493d63a'


def test_describe_eip_addresses():
    """
    Lookup a known elastic IP

    :return: None
    :rtype: None
    """
    assert len(ec2_describe.eip_addresses(
        [AWSHELPERS_NETWORK_INTERFACE], 'PublicIp')) >= 1


def test_describe_tags():
    """
    List tags of a known instance

    :return: None
    :rtype: None
    """
    assert len(ec2_describe.tags([AWSHELPERS_INSTANCE_ID])) > 0
