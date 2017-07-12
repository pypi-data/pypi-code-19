import pprint


def payload(data):
    """
    Formats Lambda event data for troubleshooting/visualizing
    
    :param data: A Lambda event object
    :type data: dict
    :return: human readable representation of event
    :rtype: str
    """
    return pprint.pprint(data)
