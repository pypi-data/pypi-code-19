from awshelpers.ec2 import _connect


def eip_addresses(ids, attribute):
    """
    Describes Elastic IP details associated with an instance or instances and filters off of attribute
    
    :param ids: network interface id(s)
    :type ids: list
    :param attribute: value to return/search for 
    :type attribute: str
    :return: a list of attributes
    :rtype: list
    """
    filters = [
        {'Name': 'network-interface-id', 'Values': ids}
    ]
    interfaces = _connect.client().describe_addresses(Filters=filters)['Addresses']

    return [interface[attribute] for interface in interfaces]

def tags(instance_ids):
    """
    Describes tags for an instance(s)

    :param resource_ids: The instance id(s)
    :type resource_ids: list
    :return: A list of dicts of tag key/values
    :rtype: list

    """
    filters = [
        {'Name': 'resource-id', 'Values': instance_ids}
    ]
    return _connect.client().describe_tags(Filters=filters)['Tags']
