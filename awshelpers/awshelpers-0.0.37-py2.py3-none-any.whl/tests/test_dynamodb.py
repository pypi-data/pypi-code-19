from awshelpers.dynamodb import item as dd_item
import datetime
import decimal

data = {
    'bounce': 12,
    'rejected': 15,
    'sent': 1000,
    'received': 3000,
    'deferred': 3000,  # deferred is a reserved word in dynamo
    'message': 'sdasdasdasa',
    'bounce_messages': [420, 'asdasd'],
    'bounce messages details': ['this is more detail', 'lots and lots of details'],
    'a_float': decimal.Decimal('3.3'),
    'a_dict': {'one': 'one', 'two': 2}
}


def test():
    """
    Attempt to upsert data in a test Dynamodb table
    
    The Dynamodb table was created in advance with Item and ItemData as a composite Primary Key.
    
    :return: None
    :rtype: None
    """
    primary_key = {'Hour': '0000-0008', 'Date': datetime.datetime.utcnow().isoformat(';').split(';')[0]}
    dynamodb_result = dd_item.upsert('awshelpers_composite_key_test', primary_key, 'Stats', data)
    assert dynamodb_result['ResponseMetadata']['HTTPStatusCode'] == 200
