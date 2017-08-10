import boto3


def check_load_balancer(arn_str):
    '''
    Input: arn str
    Output:
      0: The arn is not a load balancer
      1: The arn is classic load balancer
      2: The arn is application load balancer
    '''
    str_array = arn_str.split(':')

    # validate
    if len(str_array) < 6:
        return 0

    define_str = str_array[len(str_array) - 1]

    # case: application lb
    if define_str.startswith('loadbalancer/app/'):
        return 2

    # case: classic lb
    if define_str.startswith('loadbalancer/'):
        return 1

    # case: not lb
    return 0


def get_dns_name_by_arn(arn):
    """
    Check whether the dns is elb, alb or not

    Arguments:
        arn {string} -- input arn

    Returns:
        int -- nubmer
            0: not elb
            1: elb
            2: alb
    """
    check_lb = check_load_balancer(arn)

    # case check_lb == 0
    if check_lb == 0:
        return

    # case check_lb == 2
    client = boto3.client('elbv2')

    # case check_lb == 1
    if check_lb == 1:
        client = boto3.client('elb')

    response = client.describe_load_balancers(LoadBalancerArns=[arn])
    for lb in response['LoadBalancers']:
        return lb['DNSName']


def get_dns_name_by_tag(key, value):
    # print(key, value)
    rgsa = boto3.client('resourcegroupstaggingapi')
    response = rgsa.get_resources(TagFilters=[{'Key': key, 'Values': [value]}])

    for res in response['ResourceTagMappingList']:
        arn = res['ResourceARN']
        if check_load_balancer(arn) > 0:
            dns_name = get_dns_name_by_arn(arn)
        if bool(dns_name):
            return {'AppName': value, 'DNSName': dns_name}


def get_public_dns_name(name=None):
    results = []
    cloudformation = boto3.client('cloudformation')
    stacks = cloudformation.describe_stacks()
    for stack in stacks['Stacks']:
        # print('StackName: ', stack['StackName'])
        for tag in stack['Tags']:
            if tag['Key'] == 'empire.app.name':
                results.append(get_dns_name_by_tag(tag['Key'], tag['Value']))

    if not name:
        return results
    else:
        return [res for res in results if name in res['AppName']]
