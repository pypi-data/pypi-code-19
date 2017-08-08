import time

from ..utils.atomic_counter import AtomicCounter


class Reservoir(object):
    """
    Keeps track of the number of sampled segments within
    a single second. This class is implemented to be
    thread-safe to achieve accurate sampling.
    """
    def __init__(self, traces_per_sec=0):
        """
        :param int traces_per_sec: number of guranteed
            sampled segments.
        """
        self.traces_per_sec = traces_per_sec
        self.used_this_sec = AtomicCounter()
        self.this_sec = int(time.time())

    def take(self):
        """
        Return True if there are segments left within the
        current second, otherwise return False.
        """
        now = int(time.time())

        if now != self.this_sec:
            self.used_this_sec.reset()
            self.this_sec = now

        if self.used_this_sec.get_current() >= self.traces_per_sec:
            return False

        self.used_this_sec.increment()
        return True
