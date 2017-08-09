# coding: utf-8
import redis
import pickle
import logging
# 设置屏幕输出句柄
logger = logging.getLogger("mercury")
logger.setLevel(logging.DEBUG)


class RedisNotConnected(BaseException):
    def __init__(self, host, port):
        err = "Error connecting to redis {}:{}".format(host, port)
        super().__init__(err)

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class MercuryApp(metaclass=Singleton):
    """
    A MercuryApp is a Singleton
    """

    def __init__(
            self,
            name=None,
            redis_host="localhost",
            port=6379,
            redis_password=None
    ):
        super().__init__()
        try:
            self.__redis = redis.StrictRedis(
                host=redis_host,
                port=port,
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=3
            )
            if name is None:
                import hashlib
                import time
                import random
                name = hashlib.md5()
                name.update(str(time.time()+random.random()).encode())
                name = name.hexdigest()
            self.__redis.client_setname(name)
            self.name = name

            self.__redis.client_list()
            self.__pubsub = self.__redis.pubsub()
            self.__handlers = {}
            self.started = False
        except Exception as e:
            logger.error("{}".format(e))
            raise RedisNotConnected(host=redis_host, port=port)

    def add_handler(self, channel, handler):
        self.__handlers[channel] = handler

    def publish(self, channel, message):
        self.__redis.publish(channel, pickle.dumps(message))

    def subscribe(self, channel):
        self.__pubsub.subscribe(channel)

    def on_message(self, msg):
        print("on_message:", msg)

    def start(self):
        """
        Start a thread, keep delivering messages to handlers
        :return:
        """
        import threading
        threading.Thread(target=self.run_in_thread, daemon=True).start()

    def run_in_thread(self):
        while True:
            self.__next__()

    def __iter__(self):
        return self

    def __next__(self):
        msg = self.__pubsub.get_message(timeout=5)
        if msg is not None:
            if msg['type'] == 'message':
                data = None
                try:
                    data = pickle.loads(msg['data'])
                except TypeError:
                    logger.error("Unexpected Message Type Received: {}, a pickle".format(msg['data']))

                if data:
                    if msg["channel"] in self.__handlers:
                        handler = self.__handlers[msg["channel"]]
                        handler(data)
                    else:
                        self.on_message(data)
                    return data
