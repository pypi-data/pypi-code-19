import unittest
import mock
from botocore.stub import Stubber
from stacker.lookups.handlers.ami import handler, ImageNotFound
import boto3
from stacker.tests.factories import SessionStub


class TestAMILookup(unittest.TestCase):
    client = boto3.client("ec2", region_name="us-east-1")

    def setUp(self):
        self.stubber = Stubber(self.client)

    @mock.patch("stacker.lookups.handlers.ami.get_session",
                return_value=SessionStub(client))
    def test_basic_lookup_single_image(self, mock_client):
        image_id = "ami-fffccc111"
        self.stubber.add_response(
            "describe_images",
            {
                "Images": [
                    {
                        "OwnerId": "897883143566",
                        "Architecture": "x86_64",
                        "CreationDate": "2011-02-13T01:17:44.000Z",
                        "State": "available",
                        "ImageId": image_id,
                        "Name": "Fake Image 1",
                        "VirtualizationType": "hvm",
                    }
                ]
            }
        )

        with self.stubber:
            value = handler("owners:self name_regex:Fake\sImage\s\d")
            self.assertEqual(value, image_id)

    @mock.patch("stacker.lookups.handlers.ami.get_session",
                return_value=SessionStub(client))
    def test_basic_lookup_multiple_images(self, mock_client):
        image_id = "ami-fffccc111"
        self.stubber.add_response(
            "describe_images",
            {
                "Images": [
                    {
                        "OwnerId": "897883143566",
                        "Architecture": "x86_64",
                        "CreationDate": "2011-02-13T01:17:44.000Z",
                        "State": "available",
                        "ImageId": "ami-fffccc110",
                        "Name": "Fake Image 1",
                        "VirtualizationType": "hvm",
                    },
                    {
                        "OwnerId": "897883143566",
                        "Architecture": "x86_64",
                        "CreationDate": "2011-02-14T01:17:44.000Z",
                        "State": "available",
                        "ImageId": image_id,
                        "Name": "Fake Image 2",
                        "VirtualizationType": "hvm",
                    },
                ]
            }
        )

        with self.stubber:
            value = handler("owners:self name_regex:Fake\sImage\s\d")
            self.assertEqual(value, image_id)

    @mock.patch("stacker.lookups.handlers.ami.get_session",
                return_value=SessionStub(client))
    def test_basic_lookup_multiple_images_name_match(self, mock_client):
        image_id = "ami-fffccc111"
        self.stubber.add_response(
            "describe_images",
            {
                "Images": [
                    {
                        "OwnerId": "897883143566",
                        "Architecture": "x86_64",
                        "CreationDate": "2011-02-13T01:17:44.000Z",
                        "State": "available",
                        "ImageId": "ami-fffccc110",
                        "Name": "Fa---ke Image 1",
                        "VirtualizationType": "hvm",
                    },
                    {
                        "OwnerId": "897883143566",
                        "Architecture": "x86_64",
                        "CreationDate": "2011-02-14T01:17:44.000Z",
                        "State": "available",
                        "ImageId": image_id,
                        "Name": "Fake Image 2",
                        "VirtualizationType": "hvm",
                    },
                ]
            }
        )

        with self.stubber:
            value = handler("owners:self name_regex:Fake\sImage\s\d")
            self.assertEqual(value, image_id)

    @mock.patch("stacker.lookups.handlers.ami.get_session",
                return_value=SessionStub(client))
    def test_basic_lookup_no_matching_images(self, mock_client):
        self.stubber.add_response(
            "describe_images",
            {
                "Images": []
            }
        )

        with self.stubber:
            with self.assertRaises(ImageNotFound):
                handler("owners:self name_regex:Fake\sImage\s\d")

    @mock.patch("stacker.lookups.handlers.ami.get_session",
                return_value=SessionStub(client))
    def test_basic_lookup_no_matching_images_from_name(self, mock_client):
        image_id = "ami-fffccc111"
        self.stubber.add_response(
            "describe_images",
            {
                "Images": [
                    {
                        "OwnerId": "897883143566",
                        "Architecture": "x86_64",
                        "CreationDate": "2011-02-13T01:17:44.000Z",
                        "State": "available",
                        "ImageId": image_id,
                        "Name": "Fake Image 1",
                        "VirtualizationType": "hvm",
                    }
                ]
            }
        )

        with self.stubber:
            with self.assertRaises(ImageNotFound):
                handler("owners:self name_regex:MyImage\s\d")
