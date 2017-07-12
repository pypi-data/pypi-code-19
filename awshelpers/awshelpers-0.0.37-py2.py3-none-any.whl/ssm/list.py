from awshelpers.ssm import _connect


def command_invocations(command_id):
    """
    Provide status about a commands execution
    
    :param command_id: command id to lookup
    :type command_id: str
    :return: specific details of a commands execution
    :rtype: dict
    """
    return _connect.client().list_command_invocations(CommandId=command_id)
