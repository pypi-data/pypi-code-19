import threading
from time import sleep


class HeartBeatSender(threading.Thread):
    HEART_BEAT_TOPIC = "cypress_heart_beat"
    HEART_BEAT_INTERVAL_IN_SECS = 30

    def __init__(self, redis, app_name, version):
        threading.Thread.__init__(self)
        from cypress_common.cypress_cache import CypressCache
        self.redis = CypressCache(redis).redis
        self.app_name = app_name
        self.version = version
        self.__stop = False
        self.daemon = True

    def run(self):
        while not self.__stop:
            self.redis.publish(HeartBeatSender.HEART_BEAT_TOPIC, self.app_name + ":" + self.version)
            sleep(HeartBeatSender.HEART_BEAT_INTERVAL_IN_SECS)

    def stop(self):
        self.__stop = True
