"""
Module for AML constants
"""
import os

SUCCESS_RETURN_CODE = 0
USER_ERROR_RETURN_CODE = 1
SYSTEM_ERROR_RETURN_CODE = 2

AMBIGUOUS_RETURN_CODE = None

MMS_HOST_ACCOUNT_PROFILE = 'viennaHostAccountProfile.json'

MMS_BASE_URL = '{}/api/subscriptions/{}/resourceGroups/{}/hostingAccounts/{}/'
MMS_MANIFEST_URL = MMS_BASE_URL + 'manifests'
MMS_IMAGE_URL = MMS_BASE_URL + 'images'
MMS_SERVICE_URL = MMS_BASE_URL + 'services'
MMS_OPERATION_URL = MMS_BASE_URL + 'operations/{}'

MMS_SYNC_TIMEOUT_SECONDS = 20
MMS_ASYNC_OPERATION_POLLING_INTERVAL_SECONDS = 5
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
