class RedisCounter(EventCounter):

    def __init__(self, host, port, instance):
        self._redis = redis.StrictRedis(
            host=host,
            port=port,
        )
        self._instance_name = instance
        self._logger = logging.getLogger(__name__)

    @retry(wait_exponential_multiplier=1000, wait_exponential_max=10000, stop_max_delay=60000)
    def __getitem__(self, stream):
        self._logger.debug("Fetching last read event for stream "+stream)
        key = self._key(stream)
        val = self._redis.get(key)
        if(val):
            val = int(val)
            self._logger.info(
                "Last read event for stream %s is %d",
                stream,
                val)
            return val
        return -1

    @counter_circuit_breaker
    def __setitem__(self, stream, val):
        key = self._key(stream)
        self._redis.set(key, val)

    def _key(self, stream):
        return "urn:atomicpuppy:"+self._instance_name+":"+stream+":position"


