import logging
import os
import os.path
import sys

import yaml

from s3config import uri_manager

# ******************************
# Setup logging
# ******************************

logger = logging.getLogger(__name__)


class Config(object):
    def __init__(self, secrets_path, test_secrets_path=None, secrets_url_var_name=None):
        super(Config, self).__init__()
        # if local config file exists, load it
        if Config.is_testing():
            secrets_file = open(test_secrets_path, "r")
            self.secrets = yaml.load(secrets_file)['app_secrets']
            logger.info("Using testing secrets file")
            print("Using testing secrets file")
        elif os.path.exists(secrets_path):
            secrets_file = open(secrets_path, "r")
            self.secrets = yaml.load(secrets_file)['app_secrets']
            logger.info("Using local secrets file")
            print("Using local secrets file")
        elif os.getenv(secrets_url_var_name, None) is not None:
            secrets_file_data = uri_manager.get_resource_data_from_uri(
                os.environ[secrets_url_var_name])
            self.secrets = yaml.load(secrets_file_data)['app_secrets']
            logger.info("Using secrets url configured in the env")
            print("Using secrets url")
        else:
            logger.critical("Unable to find secrets uri...")
            print("unable to find secrets uri")
            raise Exception("unable to find secrets url...")

    def get_value(self, key):
        if key in self.secrets:
            return self.secrets[key]
        raise Exception("missing property in secrets.yml [%s]" % key)

    @staticmethod
    def is_testing():
        return 'test' in sys.argv
