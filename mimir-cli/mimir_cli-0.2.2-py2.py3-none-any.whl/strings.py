import os


MIMIR_DIR = os.path.expanduser('~/.mimir/')
API_URL = 'https://app.mimir.cloud'
CLASSROOM_URL = 'https://class.mimir.io'
AUTH_SUCCESS = 'Successfully logged into Mimir!\n'
ERR_NOT_AUTH = 'Please log in first!\n'
ERR_INVALID_CRED = 'Invalid email or password!\n'
ERR_INVALID_FILE = 'Failed to open file.\n'
PROJECT_PROMPT = 'Type the number of the project you want to submit to: '
PROJECT_ERR_0_TO_N = 'Input a number 0 through {} please!\n'
EMAIL_PROMPT = 'Email: '
