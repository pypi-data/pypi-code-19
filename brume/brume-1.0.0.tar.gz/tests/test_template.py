import unittest
import boto3
from moto import mock_s3

from brume.template import Template

CONFIG = {
    'local_path': 'test_stack',
    's3_bucket': 'dummy-bucket',
    's3_path': 'cloudformation'
}

CFN_TEMPLATE = """{
  "AWSTemplateFormatVersion": "2010-09-09",
  "Description": "test-dev-1: S3",
  "Resources": {
    "MyBucket": {
      "Properties": {
        "BucketName": "my-bucket-test-dev-1",
      },
      "Type": "AWS::S3::Bucket"
    }
  }
}
"""

class TestTemplate(unittest.TestCase):
    """
    Test for brume.Template
    """

    @mock_s3
    def test_upload(self):
        """
        A template can be uploaded to S3.
        """
        conn = boto3.resource('s3')
        conn.create_bucket(Bucket=CONFIG['s3_bucket'])
        template = Template('tests/test_stack/main.json', CONFIG)
        template.upload()
        body = conn.Object(CONFIG['s3_bucket'], 'cloudformation/tests/main.json').get()['Body'].read().decode("utf-8")
        assert body == CFN_TEMPLATE


if __name__ == '__main__':
    unittest.main()
