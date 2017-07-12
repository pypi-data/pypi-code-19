from awshelpers.ssm import send as ssm_send, get as ssm_get, list as ssm_list


def test():
    """
    Create and run a SSM command on a test EC2 instance
    
    Command should execute successfully, status amd command_invocation should return Success.
    
    :return: 
    :rtype: 
    """
    command_result = ssm_send.command(['i-073a59252f493d63a'], 'AWS-RunShellScript', 240, 'awshelpers test_commnd()',
                                      ['cd /tmp', 'date', 'ping 8.8.8.8 -c 3'], 'us-west-2', 'lasso-ops',
                                      'ssm/command-output/postfix-data-collector/')

    assert command_result['ResponseMetadata']['HTTPStatusCode'] == 200
    assert ssm_get.status(command_result['Command']['CommandId']) == 'Success'
    assert ssm_list.command_invocations(command_result['Command']['CommandId'])[u'CommandInvocations'][0][
               'Status'] == 'Success'
