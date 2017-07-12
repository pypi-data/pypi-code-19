from awshelpers.dynamodb import _connect
from botocore.exceptions import ClientError


def put(table, primary_key, item_name):
    """
    Conditionally adds an item to a Dynamodb table
    
    Checks to see if all the attributes in the primary_key exist before adding,
    if an attribute is found function returns.
    
    Primary key attribute names are 'escaped' via expression_attribute_names in order 
    to avoid dynamodb revered word errors.
    
    :param table: name of table
    :type table: str
    :param primary_key: attributes of primary key can include key or key & sort (composite key)
    :type primary_key: dict
    :param item_name: name of attribute to add to item
    :type item_name: str
    :return: True if record is added or exists, False on error
    :rtype: bool
    """
    try:
        condition_expression = []
        expression_attribute_names = {}
        for key, value in primary_key.items():
            condition_expression.append("attribute_not_exists(#{})".format(key))
            expression_attribute_names["#{}".format(key)] = key

        item_keys = {}
        item_keys.update(primary_key)
        item_keys["{}".format(item_name)] = {}

        _connect.resource().Table(table).put_item(
            Item=item_keys,
            ConditionExpression=' AND '.join(condition_expression),
            ExpressionAttributeNames=expression_attribute_names,
        )
    except ClientError as e:
        if e.response['Error']['Code'] == "ConditionalCheckFailedException":
            # record already exists
            return True
        else:
            # something else went wrong
            raise
    else:
        # record inserted
        return True


def upsert(table, primary_key, item_name, item_values):
    """
    Inserts and or updates a Dynamodb item
    
    item_values keys are 'escaped' via expression_attribute_names in order 
    to avoid dynamodb revered word errors. 
    
    :param table: name of table
    :type table: str
    :param primary_key: attributes of primary key can include key or key & sort (composite key)
    :type primary_key: dict
    :param item_name: name of attribute to add to item
    :type item_name: str
    :param item_values: complex object of values to add to item_name
    :type item_values: dict
    :return: return the updated attributes 
    :rtype: dict
    """
    put(table, primary_key, item_name)

    update_expression = ['set']
    expression_attribute_values = {}
    expression_attribute_names = {}

    for key, value in item_values.items():
        key_no_white_space = key.replace(" ", "_")
        update_expression.append("{0}.#{1} =:{2},".format(item_name, key_no_white_space, key_no_white_space))
        expression_attribute_values[":{}".format(key_no_white_space)] = value
        expression_attribute_names["#{}".format(key_no_white_space)] = key_no_white_space

    return _connect.resource().Table(table).update_item(
        Key=primary_key,
        UpdateExpression=' '.join(update_expression)[:-1],
        ExpressionAttributeNames=expression_attribute_names,
        ExpressionAttributeValues=expression_attribute_values,
        ReturnValues="UPDATED_NEW"
    )
