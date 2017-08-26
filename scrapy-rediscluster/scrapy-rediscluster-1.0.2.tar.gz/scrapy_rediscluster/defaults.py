import rediscluster


# For standalone use.
DUPEFILTER_KEY = 'dupefilter:%(timestamp)s'

PIPELINE_KEY = '%(spider)s:items'

#REDIS_CLS = rediscluster.StrictRedisCluster
REDIS_PASS='123456789a!'
REDIS_ENCODING = 'utf-8'
# Sane connection defaults.
# REDIS_PARAMS = {
#     'socket_timeout': 30,
#     'socket_connect_timeout': 30,
#     'retry_on_timeout': True,
#     'encoding': REDIS_ENCODING,
# }
# kwargs = {
#     'db': 0,
#     'password': '123456789a!',
#     'socket_timeout': 30,
#     'encoding': REDIS_ENCODING,
#     'decode_responses': True,
#     'retry_on_timeout': True,
# }
SCHEDULER_QUEUE_KEY = '%(spider)s:requests'
SCHEDULER_QUEUE_CLASS = 'newcrawler.scrapy_redis.queue.PriorityQueue'
SCHEDULER_DUPEFILTER_KEY = '%(spider)s:dupefilter'
SCHEDULER_DUPEFILTER_CLASS = 'newcrawler.scrapy_redis.dupefilter.RFPDupeFilter'

START_URLS_KEY = '%(name)s:start_urls'
START_URLS_AS_SET = False
REDIS_URLS = [{'host': '198.11.173.65', 'port': 6379},
               {'host': '198.11.173.65', 'port': 6380},
               {'host': '198.11.173.6', 'port': 6379},
               {'host': '198.11.173.6', 'port': 6380},
               {'host': '198.11.173.89', 'port': 6379},
               {'host': '198.11.173.89', 'port': 6380},
               ]
