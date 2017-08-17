import os

TYPE = 'dict'
BATCH_SIZE = 32

DATA_FILE_NAME = 'data.json'

API_URL = 'http://api.xyxy.io/' if not os.environ.get('XYXY') else os.environ.get('XYXY_API_URL')
BASE_PATH = '~/.xyxy' if not os.environ.get('XYXY') else os.environ.get('XYXY_BASE_PATH')

MONGO_URI = None
MONGO_DBNAME = 'xyxy_datasets'

MONGO_DB = None

MAX_INMEMORY_FILE_SIZE = 100  # MB
MAX_AWAIT_TIME = 128  # SEC
