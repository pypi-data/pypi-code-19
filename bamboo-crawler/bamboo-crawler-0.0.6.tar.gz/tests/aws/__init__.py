import json
import subprocess
import unittest

import boto3
import yaml


class TestAWSModules(unittest.TestCase):
    def setUp(self):
        s3 = subprocess.Popen(
            ['moto_server', 's3', '-p', '5000'],
            stderr=subprocess.PIPE)
        sqs = subprocess.Popen(
            ['moto_server', 'sqs', '-p', '5001'],
            stderr=subprocess.PIPE)
        s3.stderr.readline()
        sqs.stderr.readline()
        self.s3 = s3
        self.sqs = sqs
        with open('tests/aws/env.yml') as f:
            y = yaml.load(f.read())
        cbc = {'LocationConstraint': y['s3_config']['region_name']}
        boto_s3 = boto3.resource('s3', **y['s3_config'])
        boto_sqs = boto3.resource('sqs', **y['sqs_config'])
        boto_s3.create_bucket(Bucket='sample-bucket',
                              CreateBucketConfiguration=cbc)
        boto_sqs.create_queue(QueueName='sample-queue')

    def tearDown(self):
        s3 = self.s3
        sqs = self.sqs
        s3.kill()
        sqs.kill()
        s3.stderr.close()
        sqs.stderr.close()
        s3.wait()
        sqs.wait()

    def run_recipe(self, taskname):
        c = subprocess.run([
            'python3',
            '-m', 'bamboo_crawler',
            '-r', 'tests/aws/recipe.yml',
            '-e', 'tests/aws/env.yml',
            '-t', taskname],
            stdout=subprocess.PIPE)
        self.assertEqual(c.returncode, 0)
        return c

    def test_aws_inputter_and_outputter(self):
        self.run_recipe('aws_outputter')
        c = self.run_recipe('aws_inputter')
        j = json.loads(c.stdout)
        self.assertEqual(j['sampledata'], 'ABCDEFGHIJKLMN')
