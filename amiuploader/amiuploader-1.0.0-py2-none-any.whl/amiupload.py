#!/usr/bin/python
import argparse
import os
import sys
import tempfile

import AWSUtilities


# TODO: Add licensing
# arg validation
# pypi packaging info
# requirements
# readmes


def parse_args():
    """
    Argument parser and validator
    """
    parser = argparse.ArgumentParser(description="Uploads specified VMDK file to AWS s3 bucket, and converts to AMI")
    parser.add_argument('-r', '--aws_regions', type=str, nargs='+', required=True,
                        help='list of AWS regions where uploaded ami should be copied. Available'
                             ' regions: {}.'.format(AWSUtilities.aws_regions))
    parser.add_argument('-a', '--aws_profile', type=str, required=True, help='AWS profile name to use for aws cli commands')
    parser.add_argument('-b', '--s3_bucket', type=str, required=True,
                        help='The aws_bucket of the profile to upload and save vmdk to')
    parser.add_argument('-f', '--vmdk_upload_file', type=str, required=True,
                        help="The file to upload if executing ")
    parser.add_argument('-n', '--ami_name', type=str, required=False, help='The name to give to the uploaded ami. '
                                                                           'Defaults to the name of the file')
    parser.add_argument('-d', '--directory', type=str, default=tempfile.mkdtemp(),
                        help='Directory to save temp aws config upload files')
    args = parser.parse_args()

    if not args.ami_name:
        args.ami_name = os.path.basename(args.vmdk_upload_file)

    validate_args(args)

    return args


def validate_args(args):
    """
    Perform necessary validation checks
    :param args:
    :return:
    """
    # print size of vm to be dl, if dl dir exists, check that file to uplad is a vmdk
    if not os.path.isdir(args.directory):
        print "Directory {} does not exist".format(args.directory)
        sys.exit(5)

    try:
        args.vmdk_upload_file = args.vmdk_upload_file
    except AttributeError:
        args.vmdk_upload_file = None

    if args.vmdk_upload_file and not os.path.isfile(args.vmdk_upload_file):
        print "Specified file: {} does not exist".format(args.vmdk_upload_file)
        sys.exit(5)

    aws_importer = AWSUtilities.AWSUtils(args.directory, args.aws_profile, args.s3_bucket,
                                         args.aws_regions, args.ami_name, args.vmdk_upload_file)
    aws_importer.validate()


def vmdk_to_ami(args):
    """
    Calls methods to perform vmdk import
    :param args:
    :return:
    """
    aws_importer = AWSUtilities.AWSUtils(args.directory, args.aws_profile, args.s3_bucket,
                                         args.aws_regions, args.ami_name, args.vmdk_upload_file)
    aws_importer.import_vmdk()

def main():
    args = parse_args()
    vmdk_to_ami(args)


if __name__ == "__main__":
    main()