#!/usr/bin/env python
"""
------------------------------------------------------------------------------
Name:        managerThread
Author:      Sean Wiseman
------------------------------------------------------------------------------
"""

from time import sleep
from inspect import signature
import threading

try:
    import Queue as queue
except ImportError:
    import queue


__version__ = "1.0.0"


class ManagerThread(object):
    """A utility Thread wrapper which starts a thread that manages
        a queue and passes queue entries to be processed a by user
        defined function.
    """

    # TODO integrate with logging module

    instances = []

    def __init__(self, name='ManagerThreadInstance', target_func=None, timeout=0.1, daemon=True, *args, **kwargs):
        """
        args:
            name        --
            target_func --
            log_q       --
            timeout     --
            daemon      --
        """
        ManagerThread.instances.append(self)
        self.name = name
        self.__alive = False
        self.__lock = threading.Lock()
        self.queue = queue.Queue()
        self.__timeout = timeout
        self.target_func = self.assign_target_func(target_func)
        self.worker_thread = threading.Thread(
            target=self.__worker,
            name=self.name
        )
        self.worker_thread.daemon = daemon

    def is_alive(self):
        return self.__alive

    @staticmethod
    def assign_target_func(func):
        """Make sure func is a callable object that accepts args"""
        if callable(func) and len(signature(func).parameters):
            return func
        else:
            raise ValueError('Target function is not callable')

    def start(self):
        self.__alive = True
        self.worker_thread.start()

    def stop(self):
        """ stop worker thread """
        self.__alive = False

    def __worker(self):
        """Watches self.queue and executes
        self.target_func on delivery of new data
        """
        while self.__alive:
            try:
                sleep(self.__timeout)
                data = self.queue.get(block=False)
            except queue.Empty:
                pass
            else:
                try:
                    self.__lock.acquire()
                    self.target_func(data)
                    sleep(self.__timeout)
                except Exception as err:
                    # TODO integrate with logging module
                    raise err
                finally:
                    self.__lock.release()

    @classmethod
    def start_all_threads(cls):
        for thread in cls.instances:
            thread.start()

    @classmethod
    def stop_all_threads(cls):
        for thread in cls.instances:
            thread.stop()

    @classmethod
    def thread_statuses(cls):
        return {t.name: t.__alive for t in cls.instances}


if __name__ == '__main__':
    pass
