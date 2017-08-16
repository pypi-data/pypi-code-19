"""
Module for AML constants
"""
import os

SUCCESS_RETURN_CODE = 0
USER_ERROR_RETURN_CODE = 1
SYSTEM_ERROR_RETURN_CODE = 2

AMBIGUOUS_RETURN_CODE = None

MMS_HOST_ACCOUNT_PROFILE = 'viennaHostAccountProfile.json'

MMS_BASE_URL_FMT = '{}/api/subscriptions/{}/resourceGroups/{}/hostingAccounts/{}/'
MMS_MODEL_URL_FMT = MMS_BASE_URL_FMT + 'models'
MMS_MANIFEST_URL_FMT = MMS_BASE_URL_FMT + 'manifests'
MMS_IMAGE_URL_FMT = MMS_BASE_URL_FMT + 'images'
MMS_SERVICE_URL_FMT = MMS_BASE_URL_FMT + 'services'
MMS_SERVICE_LIST_KEYS_URL_FMT = MMS_SERVICE_URL_FMT + '/{}/keys'
MMS_SERVICE_REGEN_KEYS_URL_FMT = MMS_SERVICE_URL_FMT + '/{}/regenerateKeys'
MMS_OPERATION_URL_FMT = MMS_BASE_URL_FMT + 'operations/{}'

MMS_SYNC_TIMEOUT_SECONDS = 20
MMS_ASYNC_OPERATION_POLLING_INTERVAL_SECONDS = 5
MMS_ASYNC_OPERATION_POLLING_MAX_TRIES = 5
MMS_IMAGE_CREATE_OPERATION_POLLING_MAX_TRIES = 120
MMS_SERVICE_CREATE_OPERATION_POLLING_MAX_TRIES = 120

POSSIBLE_SKU_NAMES = ['F0', 'P0', 'P1', 'P2', 'S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6']
POSSIBLE_SKU_TIERS = ['Free', 'Basic', 'Standard', 'Premium']

DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
SERVICE_DATA_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'service', 'data')
SUPPORTED_RUNTIMES = ['spark-py', 'cntk-py', 'tlc', 'scikit-py']
NINJA_RUNTIMES = ['mrs']
CREATE_CMD_SAMPLE = "az ml service create realtime -f <webservice file> -n <service name> [--model-file <model1> [--model-file <model2>] ...] [-p requirements.txt] [-d <dependency> [-d <dependency>] ...] [-s <schema>] [-r {0}] [-l] [-z <replicas>] [--collect-model-data]".format("|".join(SUPPORTED_RUNTIMES))  # pylint: disable=line-too-long
SCORING_URI_FORMAT = "{0}/score"
SWAGGER_URI_FORMAT = "{0}/swagger.json"
DEFAULT_INPUT_DATA = "!! YOUR DATA HERE !!"

# config keys
CURRENT_COMPUTE_CONFIG_KEY = 'current_config'
COMPUTE_NAME_KEY = 'name'
COMPUTE_RG_KEY = 'rg'
COMPUTE_FE_URL_KEY = 'fe_url'
MODE_KEY = 'mode'
LOCAL = 'local'
CLUSTER = 'cluster'

# path to machinelearningcompute base
# allowing from removing client code from source eventually
MLC_SDK_PATH = '._machinelearningcompute'
MLC_CLIENT_PATH = '{}.machine_learning_compute_management_client'.format(MLC_SDK_PATH)
MLC_MODELS_PATH = '{}.models'.format(MLC_SDK_PATH)
MLC_CLIENT_ENUMS_PATH = '{}.machine_learning_compute_management_client_enums'.format(MLC_MODELS_PATH)
