#!/usr/bin/env python
#
# Syntax: awssu [-i] [-s 3600] <aws_profile_name>
#

import argparse
import boto3
import botocore
import os
import sys

# For python 2.7 and 3 support
try:
    from configparser import configparser
except ImportError:
    from ConfigParser import ConfigParser as configparser


def su(cmd_args):
    config = read_config(cmd_args.profile)
    credentials = assume_role(config, cmd_args.session_timeout)

    if cmd_args.in_place:
        update_credentials(cmd_args.profile, credentials)
    else:
        print_exports(cmd_args.command, cmd_args.profile, credentials)


def read_config(profile):
    """This reads our config files automatically, and combines config and
    credentials files for us"""
    profiles = botocore.session.get_session().full_config.get('profiles', {})

    # Checks for the passed in profile, mostly for sanity
    if profile not in profiles:
        print("Profile '%s' does not exist in the config file." % profile)
        quit(2)

    if (
        'role_arn' not in profiles[profile] or
        'source_profile' not in profiles[profile]
    ):
        print(
            "Profile '%s' does not have role_arn "
            "or source_profile set." % profile
        )
        quit(3)

    return profiles[profile]


def print_exports(command, profile, credentials):
    # Unset variables for sanity sake
    print('unset AWS_DEFAULT_PROFILE')
    print('unset AWS_PROFILE')
    print('unset AWS_ACCESS_KEY_ID')
    print('unset AWS_SECRET_ACCESS_KEY')
    print('unset AWS_SESSION_TOKEN')
    print('unset AWS_SECURITY_TOKEN')

    # Set AWS/Boto environemnt variables before executing target command
    print('export AWS_ACCESS_KEY_ID=' + (credentials['AccessKeyId']))
    print('export AWS_SECRET_ACCESS_KEY=' + (credentials['SecretAccessKey']))
    print('export AWS_SESSION_TOKEN=' + (credentials['SessionToken']))
    print('export AWS_SECURITY_TOKEN=' + (credentials['SessionToken']))


def update_credentials(profile, credentials):
    credentials_file = os.path.expanduser('~/.aws/credentials')
    config = configparser()
    config.read(credentials_file)

    # Create profile section in credentials file
    if not config.has_section(profile):
        config.add_section(profile)

    # Set access credentials
    # `aws_security_token` is used by boto
    # `aws_session_token` is used by aws cli
    config.set(
        profile, 'aws_access_key_id', credentials['AccessKeyId'])
    config.set(
        profile, 'aws_secret_access_key', credentials['SecretAccessKey'])
    config.set(
        profile, 'aws_session_token', credentials['SessionToken'])
    config.set(
        profile, 'aws_security_token', credentials['SessionToken'])

    # Update credentials file
    with open(credentials_file, 'w') as credentials_file:
        config.write(credentials_file)

    print(
        "Aws credentials file got updated with temporary access for profile %s"
        % profile
    )


def assume_role(config, session_timeout):
    role_arn = config['role_arn']

    if 'region' in config:
        os.putenv('AWS_DEFAULT_REGION', config['region'])
        os.putenv('AWS_REGION', config['region'])

    # Create a session using profile or EC2 Instance Role
    # To use Instance Role set `source_profile` to empty string in aws profile
    # configuration file
    session = boto3.Session(profile_name=(config['source_profile'] or None))

    # Assume role using STS client
    sts_client = session.client('sts')
    if 'mfa_serial' in config:
        token = raw_input("Enter MFA token: ")
        assumedRoleObject = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="AssumeRoleSession",
            DurationSeconds=session_timeout,
            SerialNumber=config['mfa_serial'],
            TokenCode=token
        )
    else:
        assumedRoleObject = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName="AssumeRoleSession",
            DurationSeconds=session_timeout
        )

    print(
        "Assumed '%s' role using '%s' profile\nExpiration Token: %s"
        % (
            role_arn,
            config['source_profile'],
            str(assumedRoleObject['Credentials']['Expiration'])
        )
    )

    return assumedRoleObject['Credentials']


class CommandParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()
        sys.stderr.write('error: %s\n' % message)
        sys.exit(2)


def command():
    parser = CommandParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""description:
'su' but with AWS profiles.
    """
    )

    parser.add_argument(
        '-i', '--in-place',
        dest='in_place',
        help='Should we udpate ~/.aws/credentials with tmp credentials',
        action='store_true'
    )

    parser.add_argument(
        '-s', '--session-timeout',
        dest='session_timeout',
        help='STS session timeout in seconds in the range 900..3600',
        type=int,
        default=3600
    )

    parser.add_argument(
        'profile',
        help='Name of the AWS profile',
        default=''
    )

    parser.add_argument(
        'command',
        nargs='*',
        help='Command to be executed',
    )

    cmd_args, _ = parser.parse_known_args()

    su(cmd_args)


def main():
    command()
