import boto3

iam_client = boto3.client('iam')

ASSUMED_ROLE_POLICY = """{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "lambda.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}"""

POLICY = """{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "kinesis:GetRecords",
                "kinesis:GetShardIterator",
                "kinesis:DescribeStream",
                "kinesis:ListStreams",
                "kinesis:PutRecord",
                "logs:CreateLogGroup",
                "firehose:*",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}"""


def create_firehoser_role(role_name='firehoser_role'):
    try:
        response = iam_client.create_role(
                Path='/',
                RoleName=role_name,
                AssumeRolePolicyDocument=ASSUMED_ROLE_POLICY
        )
    except iam_client.exceptions.EntityAlreadyExistsException:
        response = iam_client.get_role(RoleName=role_name)

    return response


def put_firehoser_role_policy(role_name='firehoser_role', policy_name='firehoser_policy'):
    try:
        response = iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=POLICY
        )
    except iam_client.exceptions.EntityAlreadyExistsException:
        response = iam_client.get_role_policy(RoleName=role_name, PolicyName=policy_name)

    return response
