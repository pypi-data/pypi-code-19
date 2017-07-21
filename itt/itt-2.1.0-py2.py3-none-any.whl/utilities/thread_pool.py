import logging
from Queue import Queue
from threading import Thread
from multiprocessing import cpu_count


class Worker(Thread):

    """Thread executing tasks from a given tasks queue"""

    def __init__(self, tasks):

        super(Worker, self).__init__()

        self.__stop = True

        self.tasks = tasks
        self.daemon = True

        self.start()

    def run(self):

        self.__stop = False

        while not self.__stop:

            func, args, kwargs = self.tasks.get()

            try:
                func(*args, **kwargs)

            except Exception as err:
                logging.exception(err)

            self.tasks.task_done()

    def stop(self):
        self.__stop = True


class ThreadPool:

    """Pool of threads consuming tasks from a queue"""

    def __init__(self,
                 threads=cpu_count()):

        self.tasks = Queue()
        self.workers = []

        # Setup worker threads
        for _ in range(threads):
            self.workers.append(Worker(self.tasks))

    def add_task(self, func, args=None, kwargs=None):
        """Add a task to the queue"""

        args = () if not args else args
        kwargs = {} if not kwargs else kwargs

        self.tasks.put((func, args, kwargs))

    def join(self):
        """Wait for completion of all the tasks in the queue"""
        #self.tasks.join()
        for worker in self.workers:
            worker.join()

    def close(self):
        """ Signal worker threads to shutdown """
        for worker in self.workers:
            worker.stop()


if __name__ == '__main__':
    from random import randrange
    delays = [randrange(1, 10) for i in range(100)]

    from time import sleep
    def wait_delay(d):
        print 'sleeping for (%d)sec' % d
        sleep(d)

    # 1) Init a Thread pool with the desired number of threads
    pool = ThreadPool(20)

    for i, d in enumerate(delays):
        # print the percentage of tasks placed in the queue
        print '%.2f%c' % ((float(i)/float(len(delays)))*100.0, '%')

        # 2) Add the task to the queue
        pool.add_task(wait_delay, (d,))

    # 3) Wait for completion
    pool.close()
    pool.join()
