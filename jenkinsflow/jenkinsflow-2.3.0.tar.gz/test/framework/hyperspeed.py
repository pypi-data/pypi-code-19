import time as real_time


class HyperSpeed(object):
    def __init__(self, speedup, **kwargs):
        super(HyperSpeed, self).__init__()
        assert isinstance(speedup, int)
        self.speedup = speedup

    def time(self):
        return real_time.time() * self.speedup

    def sleep(self, seconds):
        return real_time.sleep(seconds / float(self.speedup))
