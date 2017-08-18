
class Event(object):
    def __init__(self):
        self.__propagation_stopped = False

    def is_propagation_stopped(self):
        return self.__propagation_stopped

    def stop_propagation(self):
        self.__propagation_stopped = True
