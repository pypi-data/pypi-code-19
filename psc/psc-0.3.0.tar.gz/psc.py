#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import argparse
import pipes
import re
import subprocess
import sys
import boto3
import botocore
from prettytable import PrettyTable

"""
DEFAULT_PATTERN is used to detect the keys to decrypt in the envrionment vars
Default is "SECRET (.+)"
It will be used in this matching pattern: "^(\w+)\={DEFAULT_PATTERN}$"
If you want to ustomize it, the group needs to specify the ssm parameter ID to retrieve the value from.
"""
DEFAULT_ENV_KEY_PATTERN = "SECRET (.+)"


def get_parser():
    # if no arguments, print help
    if len(sys.argv) < 2:
        sys.argv.append("-h")

    parser = argparse.ArgumentParser(description='A cli credential/secret storage utility using EC2 SSM')
    subparsers = parser.add_subparsers(help="""
                Try commands like "{name} get -h" or "{name} put --help" to get each sub command's options
                """.format(name=sys.argv[0]))

    parent_parser = argparse.ArgumentParser(add_help=False)

    parent_parser.add_argument('-r', '--region', dest='region', required=False, help="""
                The AWS region in which to operate. If a region is not specified, the default aws-cli region will be used.
                If unset, and a profile is given, then the profile's default region will be used.
                """)

    role_parse = parent_parser.add_mutually_exclusive_group()
    role_parse.add_argument('-p', '--aws-profile', '--profile', default=None, dest='aws_profile',
                            help="AWS-cli/Boto config profile to use when connecting to AWS")
    role_parse.add_argument('--arn', '--role', default=None, help="AWS IAM ARN for AssumeRole")

    parent_parser.add_argument('-d', '--debug', dest='debug', default=False, action='store_true', help="""
                If set, echo the SSM command run (beware, for `set`, the secret will appear in the logs.)
                """)

    parser_de = subparsers.add_parser('decrypt-env', parents=[parent_parser], help="""
                Scan the calling environment variables and generate export statements to replace the ones whose values match 'SECRET secret_id' with the decrypted value matching secret_id.
                """)
    parser_de.add_argument('--pattern', default=None, dest='pattern', help="""
                Custom regex portion, if you want to use a pattern different than '{}' to detect the env vars to decrypt.
                """.format(DEFAULT_ENV_KEY_PATTERN))
    parser_de.set_defaults(action='decrypt-env')

    parser_ls = subparsers.add_parser('ls', parents=[parent_parser], help="""
                List the credentials in the store
                """)
    parser_ls.set_defaults(action='ls')
    parser_ls.add_argument('-l', '--long', dest='long', default=False, action='store_true', help="""
                If set, add the description, keyId, last modification date and user to the output.
                """)
    parser_ls.add_argument('-k', '--key-id', dest='key_id', default=None, help="""
                Specify an IAM encryption key Id or alias if you don't want to use the default 'aws/ssm' one.
                Valid values are either ids like '4d2bc28b-642a-843d-45a3-7d81eb8adc78' or aliases like 'alias/myKeyName'
                """)
    parser_ll = subparsers.add_parser('ll', parents=[parent_parser], help="""
                List the credentials in the store with the details (short-hand notation for ls -l)
                """)
    parser_ll.set_defaults(action='ll', long=True)
    parser_ll.add_argument('-k', '--key-id', dest='key_id', default=None, help="""
                Specify an IAM encryption key Id or alias if you don't want to use the default 'aws/ssm' one.
                Valid values are either ids like '4d2bc28b-642a-843d-45a3-7d81eb8adc78' or aliases like 'alias/myKeyName'
                """)

    parser_get = subparsers.add_parser('get', parents=[parent_parser], help="""
                Get a credential from the store
                """)
    parser_get.set_defaults(action='get')
    parser_get.add_argument('secret_name', type=str, help="""
                The name of the secret to get from the store.""")

    parser_set = subparsers.add_parser('set', parents=[parent_parser], help="""
                Put a credential into the store
                """)
    parser_set.set_defaults(action='set')
    parser_set.add_argument('secret_name', type=str, help="""
                The name of the secret to store.
                Restriction: a secret name must be unique within a region.
                Recommended naming scheme is like '{environmentName}.{applicationName}.{secretKey}', like 'staging.myapp.DB_URL'
                """)
    parser_set.add_argument('secret_value', type=str, help="""
                The name of the credential to store
                """)
    parser_set.add_argument('--description', required=False, help="""
                The description will be stored with the key and value in the Parameter Store
                """)
    parser_set.add_argument('-k', '--key-id', dest='key_id', default=None, help="""
                Specify an IAM encryption key Id or alias if you don't want to use the default 'aws/ssm' one.
                Valid values are either ids like '4d2bc28b-642a-843d-45a3-7d81eb8adc78' or aliases like 'alias/myKeyName'
                """)

    parser_del = subparsers.add_parser('delete', parents=[parent_parser], help="""
                Delete a credential from the store
                """)
    parser_del.set_defaults(action='delete')
    parser_del.add_argument('secret_name', type=str, help="""
                The name of the secret to delete from the store.""")

    return parser


def run_sh(command):
    return subprocess.Popen(command, stdout=subprocess.PIPE, shell=True).communicate()


def clean_fail(func):
    '''
    A decorator to cleanly exit on a failed call to AWS.
    catch a `botocore.exceptions.ClientError` raised from an action.
    This sort of error is raised if you are using invalid credentials, profile, ...
    '''
    def func_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except botocore.exceptions.ClientError as err:
            sys.stderr.write(str(err) + "\n")
            sys.exit(1)
        except botocore.exceptions.NoRegionError as err:
            sys.stderr.write(str(err) + "\n")
            sys.exit(1)
    return func_wrapper


def print_debug(str, settings):
    if settings.debug:
        print_stdout("DEBUG: %s" % str)


def print_stdout(s):
    sys.stdout.write(str(s))
    sys.stdout.write("\n")


def print_stderr(s):
    sys.stderr.write(str(s))
    sys.stderr.write("\n")


def get_assumerole_credentials(arn):
    sts_client = boto3.client('sts')
    # TODO allow a mfa arn as argument, then use the code below
    # Prompt for MFA time-based one-time password (TOTP)
    # mfa_TOTP = raw_input("Enter the MFA code: ")
    assumed_role_obj = sts_client.assume_role(RoleArn=arn,
                                              RoleSessionName='AssumeRoleCredstashSession1')
    # mfa_serial_number="arn:aws:iam::ACCOUNT-NUMBER-WITHOUT-HYPHENS:mfa/MFA-DEVICE-ID",
    # mfa_token=mfa_TOTP)
    credentials = assumed_role_obj['Credentials']
    return dict(aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'])


def get_boto_session_params(profile, arn):
    params = {}
    if profile is None and arn:
        params = get_assumerole_credentials(arn)
    elif profile:
        params = dict(profile_name=profile)
    return params


def get_boto_session(aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None, profile_name=None):
    if get_boto_session._cached_session is None:
        get_boto_session._cached_session = boto3.Session(aws_access_key_id=aws_access_key_id,
                                                         aws_secret_access_key=aws_secret_access_key,
                                                         aws_session_token=aws_session_token,
                                                         profile_name=profile_name)
    return get_boto_session._cached_session
get_boto_session._cached_session = None


def set_secret(name, value, description, context):
    params = dict(Name=name, Value=value, Type='SecureString', Overwrite=True)
    if description is not None:
        params['Description'] = description
    if context.key_id is not None:
        params['KeyId'] = context.key_id
    response = context.ssm.put_parameter(**params)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print_stdout("Successfully stored secret {} (description:{}).".format(name, description))
    else:
        print_stderr("Error while pushing secret: {}".format(response))


def get_secrets(names, context):
    res = {}
    for names_by_10 in [names[x:x+10] for x in xrange(0, len(names), 10)]:
        response = context.ssm.get_parameters(Names=names_by_10, WithDecryption=True)
        if len(response['Parameters']):
            for parameter in response['Parameters']:
                res[parameter['Name']] = parameter['Value']
    return res


def get_secret(name, context):
    res = get_secrets([name], context)
    return res[name] if name in res else ''


def delete_secret(name, context):
    response = context.ssm.delete_parameter(Name=name)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print_stdout("Successfully deleted secret {}.".format(name))
    else:
        print_stderr("Error while deleting secret {}: {}".format(name, response))


def list_secrets(long, context):
    class ListRequestsContext(object):
        """ Method-restricted class to store the context during pagination
        """
        def __init__(self, boto_ctx):
            filters = [{'Key': 'Type', 'Values': ['SecureString']}]
            if boto_ctx.key_id is not None:
                filters.append({'Key': 'KeyId', 'Values': [boto_ctx.key_id]})
            self.aws_args = {"Filters":filters}
            self.next_token = None
            self.all_parameters = []

    def ssm_describe_parameters(arg_dict):
        return context.ssm.describe_parameters(**arg_dict)

    def fetch_param_page(list_req_ctx):
        response = ssm_describe_parameters(list_req_ctx.aws_args)
        list_req_ctx.next_token = response['NextToken'] if "NextToken" in response else None
        if response['ResponseMetadata']['HTTPStatusCode'] != 200:
            print_stderr("Error while listing secrets: {}".format(response))
        else:
            list_req_ctx.all_parameters += response['Parameters']

    req_ctx = ListRequestsContext(context)
    fetch_param_page(req_ctx)
    while req_ctx.next_token is not None:
        req_ctx.aws_args["NextToken"] = req_ctx.next_token
        fetch_param_page(req_ctx)

    # Format the output
    if long:
        pretty_table = PrettyTable(['Name', 'Description', 'Key', 'Last modification'])
        pretty_table.align = 'l'
        for secret in req_ctx.all_parameters:
            descr = secret['Description'] if 'Description' in secret else ''
            pretty_table.add_row([secret['Name'], descr, secret['KeyId'], "{} by {}".format(secret['LastModifiedDate'], secret['LastModifiedUser'])])
        return pretty_table
    else:
        return "\n".join([x['Name'] for x in req_ctx.all_parameters])


def decrypt_env(pattern, context):
    (raw_env, err) = run_sh("env")
    # Prepare list of secrets to collect
    keys = []
    key_to_env = dict()

    if pattern is None:
        pattern = DEFAULT_ENV_KEY_PATTERN
    matches = re.finditer(r"^(\w+)\=" + pattern + "$", raw_env, re.MULTILINE)

    for num, match in enumerate(matches):
        (env_var_name, secret_key) = match.group(1, 2)
        key_to_env[secret_key] = env_var_name
        keys.append(secret_key)
    print_debug("Keys found in env: {}".format(keys), context)
    if not len(keys):
        return
    # Decrypt the secret in a single API call
    key_to_values = get_secrets(keys, context)
    # Prepare the env export
    for key in key_to_values:
        print_debug("decrypted '{key}' from '{secret_key}' to '{val}'".format(
            key=key_to_env[key], secret_key=key, val=key_to_values[key]), context)
        print_stdout("export {}={}".format(key_to_env[key], pipes.quote(key_to_values[key])))


class SessionContext(object):
    def __init__(self, opts, **kwargs):
        session = get_boto_session(**get_boto_session_params(opts.aws_profile, opts.arn))
        if opts.region is None:
            ssm = session.client('ssm')
        else:
            ssm = session.client('ssm', region_name=opts.region)
        self.boto_session = session
        self.ssm = ssm
        self.debug = opts.debug
        self.region = opts.region
        self.key_id = opts.key_id if 'key_id' in opts else None
        self.__dict__.update(kwargs)


@clean_fail
def main():
    parsers = get_parser()
    args = parsers.parse_args()
    session_context = SessionContext(args)

    # Missing actions to add:
    # - "put" as as alias to "set"
    # - history :name :trailName :trailRegion to query Cloudwatch logs for {$.eventSource="ssm.amazonaws.com"} and
    #   then prepare the output

    if "action" in vars(args):
        if args.action == "get":
            print_stdout(get_secret(args.secret_name, session_context))
            return

        if args.action == "set":
            set_secret(args.secret_name, args.secret_value, args.description, session_context)
            return

        if args.action == "delete":
            delete_secret(args.secret_name, session_context)
            return

        if args.action in ["ls", "ll"]:
            print_stdout(list_secrets(args.long, session_context))
            return

        if args.action == "decrypt-env":
            decrypt_env(args.pattern, session_context)
            return

if __name__ == '__main__':
    main()
