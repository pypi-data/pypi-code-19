import base64
import logging
import os
import shutil
import subprocess
import sys
from ConfigParser import SafeConfigParser

import boto3
from botocore.exceptions import ClientError
import configargparse
import pkg_resources


BLESS_CA_KEY = 'Bless CA'
CA_DEST = 'lambda_configs/bless_ca.pem'
CFG_DEST = 'lambda_configs/bless_deploy.cfg'
PUBLISH_DEST = 'publish/bless_lambda.zip'


def config(args):
    boto3_session = boto3.session.Session(region_name=args.region,
                                          profile_name=args.profile)
    client = boto3_session.client('kms')
    kms_response = client.encrypt(KeyId=args.kms_key,
                                  Plaintext=args.ca_private_key_passphrase)
    encrypted_password = base64.b64encode(kms_response['CiphertextBlob'])

    cfg_file = pkg_resources.resource_filename('bless_deployer',
                                               'data/deploy.cfg')

    cfg_parser = SafeConfigParser()
    cfg_parser.read(cfg_file)

    cfg_parser.set(BLESS_CA_KEY, args.region + '_password', encrypted_password)
    cfg_parser.set(BLESS_CA_KEY, 'ca_private_key_file', 'bless_ca.pem')
    cfg_parser.write(open(args.output_file, 'w'))


def deploy(args):
    if not os.path.exists('lambda_configs'):
        os.mkdir('lambda_configs')

    shutil.copy(args.cfg_file, CFG_DEST)
    shutil.copy(args.ca_private_key_file, CA_DEST)
    os.chmod(CA_DEST, 444)

    if args.build:
        subprocess.check_call('make lambda-deps', shell=True)

    subprocess.check_call('make publish', shell=True)

    upload(args)


def upload(args):
    boto3_session = boto3.session.Session(region_name=args.region,
                                          profile_name=args.profile)
    client = boto3_session.client('lambda')

    try:
        client.get_function(FunctionName=args.function_name)
        function_exists = True
    except ClientError:
        function_exists = False

    new_code = open(PUBLISH_DEST, 'rb').read()

    if function_exists:
        client.update_function_code(
            FunctionName=args.function_name,
            ZipFile=new_code
        )
    else:
        if not args.role_arn:
            raise RuntimeError('Please provide Role arn to create function')

        client.create_function(
            FunctionName=args.function_name,
            Runtime='python2.7',
            Role=args.role_arn,
            Handler='bless_lambda.lambda_handler',
            Code={
                'ZipFile': new_code
            },
            Description='{} Bless'.format(args.function_name),
            Publish=True
        )


def main(args=None):
    """The main routine."""
    parser = configargparse.ArgumentParser(description='Stack generator')
    parser.add_argument('--profile', required=False,
                        help='aws profile name')
    parser.add_argument('--region', required=False,
                        help='Name of the aws region')
    parser.add_argument('--verbose', required=False, action='store_true',
                        help='Debug information for the deployment')
    parser.add_argument('--debug', required=False, action='store_true',
                        help='Debug information for the deployment')

    subparsers = parser.add_subparsers()

    parser_config = subparsers.add_parser('config')
    parser_config.set_defaults(func=config)

    parser_config.add_argument('output_file')
    parser_config.add_argument('-k', '--kms-key',
                               required=True,
                               help='Id or alias of the KMS key')
    parser_config.add_argument('-p', '--ca-private-key-passphrase',
                               required=True,
                               help='Passphrase to be encrypted using KMS')

    parser_deploy = subparsers.add_parser('deploy')
    parser_deploy.set_defaults(func=deploy)

    parser_deploy.add_argument('cfg_file',
                               help='Bless deploy configuration file')
    parser_deploy.add_argument('-c', '--deploy-args',
                               help='Deploy Arguments File')
    parser_deploy.add_argument('-f', '--function-name', required=True,
                               help='Bless Function name')
    parser_deploy.add_argument('-r', '--role-arn', required=False,
                               help='Bless Function Role arn')
    parser_deploy.add_argument('-k', '--ca_private_key_file', required=True,
                               help='Path of the key file')
    parser_deploy.add_argument('--build',
                               help='Build lambda dependencies',
                               action='store_true')

    parser_upload = subparsers.add_parser('upload')
    parser_upload.set_defaults(func=upload)
    parser_upload.add_argument('-f', '--function-name', required=True,
                               help='Bless Function name')
    parser_upload.add_argument('-r', '--role-arn', required=False,
                               help='Bless Function Role arn')

    args = parser.parse_args()

    if args.verbose or args.debug:
        log_level = logging.DEBUG if args.debug else logging.INFO
        logging.basicConfig(stream=sys.stdout, level=log_level)

    args.func(args)

if __name__ == "__main__":
    main()
