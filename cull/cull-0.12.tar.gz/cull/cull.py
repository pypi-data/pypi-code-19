import fire
import boto3
import sys
from botocore.client import ClientError
import pprint

S3 = boto3.resource('s3')


class Cull(object):
    def ec2(self, cloud, service):
        """
        Parse EC2 instances

        :param cloud: String 
        :param service: String
        :return: None
        """
        ec2 = boto3.resource('ec2')

        asc = boto3.client('autoscaling')

        filters = [
            {'Name': 'tag:cloud', 'Values': [cloud]},
            {'Name': 'tag:service', 'Values': [service]},
            # make sure instance is running
            {'Name': 'instance-state-code', 'Values': [16]}
        ]

        instance_names = [tag['Value'] for instance in ec2.instances.filter(Filters=filters) for tag in instance.tags if
                          tag['Key'] == 'Name']

        instance_ips = [
            instance.private_ip_address for instance in ec2.instances.filter(Filters=filters)]

        instance_ids = [
            instance.instance_id for instance in ec2.instances.filter(Filters=filters)]

        asc_instances = asc.describe_auto_scaling_instances(
            InstanceIds=instance_ids)

        instance_lifecycle_states = {instance.get('InstanceId', {}): instance.get('LifecycleState', {}) for instance in
                                     asc_instances['AutoScalingInstances']}

        for index, name in enumerate(instance_names):
            print "Name:" + name + " | ID:" + instance_ids[index] + " | State:" + instance_lifecycle_states.get(
                instance_ids[index], {}) + " | ssh://ubuntu@" + \
                instance_ips[index]

    def s3list(self, cloud):
        """
        Parse S3 buckets

        :param cloud: String
        :return: None
        """

        cloud_buckets = [
            bucket.name for bucket in S3.buckets.all() if cloud in bucket.name]
        print "\n".join(cloud_buckets)

    def s3delete(self):
        """
        Delete S3 bucket(s)

        :return: None 
        """
        try:
            buckets_to_delete = raw_input(
                'Bucket names (use spaces to pass multiple names)?:').split()
            print 'Are you sure? The following bucket(s) will be deleted...'
            print '\n'.join(buckets_to_delete)
            answer = raw_input('Only YES accepted:')

            if answer == 'YES':
                for bucket in buckets_to_delete:
                    try:
                        # check to see if bucket exists
                        S3.meta.client.head_bucket(Bucket=bucket)
                        bucket = S3.Bucket(bucket)
                        print 'Deleting...'
                        for key in bucket.objects.all():
                            key.delete()
                        bucket.delete()
                        print "{0} bucket deleted.".format(bucket.name)
                    except ClientError:
                        print "{0} bucket does exists or you do not have permission to {0}.".format(bucket)
            else:
                print 'Delete aborted.'
                return None
        except KeyboardInterrupt:
            print '\nCaught Ctrl-C, exiting.\n'
            sys.exit()


def main():
    fire.Fire(Cull)


if __name__ == '__main__':
    main()
