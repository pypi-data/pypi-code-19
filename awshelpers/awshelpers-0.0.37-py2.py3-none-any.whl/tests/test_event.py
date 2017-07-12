from awshelpers.event import dump as evt_dump, message as evt_message

EVENT = {"Records": [
    {"EventVersion": "1.0", "EventSubscriptionArn": "arn:aws:sns:EXAMPLE", "EventSource": "aws:sns",
     "Sns": {"SignatureVersion": "1", "Timestamp": "1970-01-01T00:00:00.000Z", "Signature": "EXAMPLE",
             "SigningCertUrl": "EXAMPLE", "MessageId": "95df01b4-ee98-5cb9-9903-4c221d41eb5e",
             "Message": '{"Foo": "Bar"}', "MessageAttributes": {"Test": {"Type": "String", "Value": "TestString"},
                                                                 "TestBinary": {"Type": "Binary",
                                                                                "Value": "TestBinary"}},
             "Type": "Notification", "UnsubscribeUrl": "EXAMPLE", "TopicArn": "arn:aws:sns:EXAMPLE",
             "Subject": "TestInvoke"}}]}


def test():
    """
    Parse a test dict event for values
    
    :return: 
    :rtype: 
    """

    assert evt_message.sns(EVENT, 'Foo') == "Bar"
