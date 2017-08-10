import sys
import boto3


def get_ec2_connection():
    try:
        return boto3.client('ec2')
    except Exception as e:
        sys.exit('Error connecting to EC2 check your AWS credentials!')


def describe_all_running_instances():
    ec2 = get_ec2_connection()
    ec2_response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-code',
                'Values': [
                    '16',  # Running State Code
                ]
            }
        ],
    )

    if "Reservations" not in ec2_response:
        sys.exit("Error talking with AWS - No 'Reservations' key in Response")

    return ec2_response


def get_instances_data(ec2_instances):
    instances = []

    for reservation in ec2_instances['Reservations']:
        for instance in reservation['Instances']:
            instance_tags = get_tags_from_instance(instance=instance)
            instance_data = {
                'InstanceId': instance['InstanceId'],
                'Name': instance_tags['Name'] if "Name" in instance_tags else '',
                'Owner': instance_tags['Owner'] if "Owner" in instance_tags else ''
            }
            instances.append(instance_data)

    return instances


def get_tags_from_instance(instance):
    instances_data_tags = {}
    if "Tags" in instance:
        for tag in instance['Tags']:
            tag_name = tag['Key']
            tag_value = tag['Value']

            # Check only tags with a value set
            if tag_value is not None:
                instances_data_tags[tag_name] = tag_value

    return instances_data_tags


def describe_all_running_instances_with_tag_and_value(tag, value):
    tag_key = "tag:{0}".format(tag)
    ec2 = boto3.client('ec2')
    ec2_response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'instance-state-name',
                'Values': ['running']
            },
            {
                'Name': tag_key,
                'Values': [value]
            }
        ],
    )

    if "Reservations" not in ec2_response:
        sys.exit("Error talking with AWS - No 'Reservations' key in Response")

    return ec2_response


def terminate_instances(instance_ids, dry_run):
    ec2 = get_ec2_connection()

    try:
        return ec2.terminate_instances(
            InstanceIds=instance_ids,
            DryRun=dry_run
        )
    except Exception as e:
        sys.exit(e.message)


def start_instances(instance_ids, dry_run):
    ec2 = get_ec2_connection()

    try:
        return ec2.start_instances(
            InstanceIds=instance_ids,
            DryRun=dry_run
        )
    except Exception as e:
        sys.exit('Error starting instances!')


def stop_instances(instance_ids, dry_run):
    ec2 = get_ec2_connection()

    try:
        return ec2.stop_instances(
            InstanceIds=instance_ids,
            DryRun=dry_run,
            Force=False
        )
    except Exception as e:
        sys.exit('Error stopping instances!')
