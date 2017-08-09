import boto3
from botocore.errorfactory import ClientError
import json
from os.path import normpath, basename, dirname


class SecretStore:

    def __init__(self, profile=None, region='us-east-1', json_values=False):

        # Check for a profile.
        if profile is not None:

            session = boto3.Session(profile_name=profile)
            self.ssm = session.client('ssm', region_name=region)

        else:

            # Use the default.
            self.ssm = boto3.client('ssm', region_name=region)

        # Retain whether JSON encoded secrets are being used.
        self.json_values = json_values

    def get_keys_for_path(self, path, recursive=False):

        try:
            response = self.ssm.describe_parameters(
                ParameterFilters=[
                    {
                        'Key': 'Path',
                        'Option': 'Recursive' if recursive else 'OneLevel',
                        'Values': [
                            path,
                        ],
                    }
                ]
            )

            # Parse out the keys.
            keys = [key['Name'] for key in response['Parameters']]

            return keys

        except ClientError as e:
            print('Parameters not found: {}'.format(e))

            return None

    def get_secrets_for_keys(self, keys=[]):

        # Check for no keys.
        if len(keys) == 0:
            return None

        try:

            # Build the request.
            response = self.ssm.get_parameters(
                Names=keys,
                WithDecryption=True
            )

            # Simplify the response.
            secrets = []
            for param in response['Parameters']:

                # Get the key.
                key = basename(normpath(param['Name']))

                # Get the value.
                value = self.decode_json_secret(param['Value']) if self.json_values else param['Value']

                secrets.append({'key': key, 'value': value})

            return secrets

        except ClientError as e:
            print('Parameters not found: {}'.format(e))

            return None

    def get_secrets_for_path(self, path, all_levels=False):

        # Collect all paths to check.
        paths = [path]
        if all_levels:
            while dirname(path) != '/':
                path = dirname(path)
                paths.append(path)

        # Collect all secrets.
        secrets = []
        for path in paths:

            # Get the keys.
            keys = self.get_keys_for_path(path)
            if len(keys) > 0:

                # Return the secrets.
                path_secrets = self.get_secrets_for_keys(keys)
                secrets.extend(path_secrets)

        return secrets

    def get_secret_for_key(self, name):

        try:

            param = self.ssm.get_parameter(
                Name=name,
                WithDecryption=True,
            )

            return self.decode_json_secret(param['Parameter']['Value']) if self.json_values \
                else param['Parameter']['Value']

        except ClientError as e:
            print('Parameter not found: {}'.format(e))

            return None

    @staticmethod
    def decode_json_secret(key, value):
        try:
            json_value = json.loads(value)
            return json_value
        except json.JSONDecodeError as e:
            print('Failed decode for {}: {}'.format(key, e))
            return value