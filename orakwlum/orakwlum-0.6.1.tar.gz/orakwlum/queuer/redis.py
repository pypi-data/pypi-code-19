# -*- coding: utf-8 -*-
__author__ = 'XaviTorello'

from .queue import oKW_Queue
from redis import Redis
from rq import use_connection, Queue, SimpleWorker

class Redis_queue (oKW_Queue):
    """
    Define how to interact with a Redis queue
    """

    __slots__ = ('host', 'port', 'name', 'type', 'password', 'connection', 'queue')

    def __init__(self, host, port, name, password=None):
        """
        Set the type to redis and connect to Redis
        """
        super().__init__(host=host, port=port, name=name)

        assert password == None or type(password) == str, "Password must be none or an string"

        self.password = password
        self.type = 'redis'

        self.connect()
        self.set_queue()

    def connect(self):
        if self.password:
            self.connection = Redis(self.host, self.port, password=self.password)
        else:
            self.connection = Redis(self.host, self.port)

        use_connection(self.connection)

    def set_queue(self):
        """
        Set the queue
        """
        self.queue = Queue(self.name)

    def enqueue(self, job, params):
        """
        Enqueu a job
        """
        return self.queue.enqueue(job, params)

    def set_worker(self):
        worker = SimpleWorker([self.queue], connection=self.queue.connection)
        worker.work(burst=True)

    def empty(self):
        """
        Clean the queue
        """
        self.queue.empty()

    def __len__(self):
        """
        Return the number of elements in the queue
        """
        return len(self.queue)

    def __eq__(self, other):
        """
        Magic method for comparing the number of elements in Queues '=' operator
        """
        return len(self.queue) == len(other.queue)

    def __lt__(self, other):
        """
        Magic method for comparing the number of elements in Queues '>' operator
        """
        return len(self.queue) < len(other.queue)

    def __gt__(self, other):
        """
        Magic method for comparing the number of elements in Queues '<' operator
        """
        return len(self.queue) > len(other.queue)

    def __le__(self, other):
        """
        Magic method for comparing the number of elements in Queues '<=' operator
        """
        return len(self.queue) <= len(other.queue)

    def __ge__(self, other):
        """
        Magic method for comparing the number of elements in Queues '>=' operator
        """
        return len(self.queue) >= len(other.queue)
