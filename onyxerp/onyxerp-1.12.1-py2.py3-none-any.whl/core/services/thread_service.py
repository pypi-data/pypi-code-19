import threading


class ThreadService(threading.Thread):

    __target = None
    __kwargs = dict()

    def __init__(self, callback, **keywargs):
        super(ThreadService, self).__init__()
        self.__target = callback
        self.__kwargs = keywargs

    def run(self):
        return self.__target(**self.__kwargs)
