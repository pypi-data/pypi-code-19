from datetime import datetime

LOG_DIR = 'logs'
LOG_PREFIX = 'log'
LOG_SUFFIX = '.txt'
ORDER_DIR = 'orders'
ORDER_PREFIX = 'order'
ORDER_SUFFIX = '.csv'
PREDICT_DIR = 'predicts'
PREDICT_PREFIX = 'predict'
PREDICT_SUFFIX = '.csv'
START_DATE = datetime.strptime('2017-05-22', '%Y-%m-%d').date()
END_DATE = datetime.strptime('2017-06-01', '%Y-%m-%d').date()
STRATEGY_TIMEOUT = 50
ORDER_HEADER = ['datetime', 'type', 'price', 'volume']