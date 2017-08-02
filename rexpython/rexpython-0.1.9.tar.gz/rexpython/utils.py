from multiprocessing import queues


class CountDownLatch(object):
    def __init__(self, count=1):
        self.count_changed = queues.Queue()
        self.count = count

    def count_down(self):
        self.count_changed.put(1)

    def await(self):
        c = self.count
        while c > 0:
            try:
                self.count_changed.get(timeout=1.)
                c = - 1
            except queues.Empty:
                pass
