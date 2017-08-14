class Timeframe(object):

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def within(self, time):
        return time >= self.start and time <= self.end

    def add(self, time):
        pass

    def subtract(self, time):
        pass
