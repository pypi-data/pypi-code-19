import logging
from os.path import expanduser

META_API_ROOT_URL = 'https://highlyprobable:8000/api/'
AI_API_ROOT_URL = 'https://highlyprobable:9013/ai/'
LOG_PATH = expanduser('~/hpcli.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=LOG_PATH,
    filemode='w'
)
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

