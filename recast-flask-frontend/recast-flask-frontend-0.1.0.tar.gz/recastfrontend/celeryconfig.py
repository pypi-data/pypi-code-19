from recastfrontend.frontendconfig import config as frontendconf

BROKER_URL = frontendconf['REDISURL']
CELERY_RESULT_BACKEND = frontendconf['REDISURL']
