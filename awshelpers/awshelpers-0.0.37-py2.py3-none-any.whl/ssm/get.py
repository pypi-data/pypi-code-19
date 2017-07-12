import time
from awshelpers.ssm import _connect


def status(command_id):
    """
    Polls SSM service until command completes
    
    :param command_id: id of command to get status
    :type command_id: str
    :return: status
    :rtype: str
    """
    status = 'Pending'
    while status == 'Pending' or status == 'InProgress':
        time.sleep(3)
        status = (_connect.client().list_commands(CommandId=command_id))['Commands'][0]['Status']

    return status
