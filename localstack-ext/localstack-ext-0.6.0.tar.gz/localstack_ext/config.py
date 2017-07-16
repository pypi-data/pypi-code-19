import os
from localstack import config as localstack_config
from localstack import constants as localstack_constants
from localstack.config import HOSTNAME, USE_SSL

# version of LocalStack extended
VERSION = '0.6.0'

API_SERVER = 'api.localstack.cloud'
API_PORT = 8182
API_PATH = '/v1'
API_URL = 'https://%s:%s%s' % (API_SERVER, API_PORT, API_PATH)

ROOT_FOLDER = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

PROTECTED_FOLDERS = ('services', )

# add default service ports
localstack_constants.DEFAULT_SERVICE_PORTS['cognito-idp'] = 4590
localstack_constants.DEFAULT_SERVICE_PORTS['cognito-identity'] = 4591
localstack_constants.DEFAULT_SERVICE_PORTS['sts'] = 4592

# re-initialize configs in localstack
localstack_config.populate_configs()
