import json

def sns(event, attribute):
    """
    Gets specific attributes of a SNS Message
    
    We are expecting an event object created via a SNS
    topic. Within that payload resides a u'Message' value.
    
    :param event: A Lambda event object
    :type event: dict
    :param attribute: attribute within Message value
    :type attribute: str
    :return: value of the key being looked up
    :rtype: str
    """
    message = event[u'Records'][0][u'Sns'][u'Message']
    message_data = json.loads(message)
    return message_data.get(attribute)
