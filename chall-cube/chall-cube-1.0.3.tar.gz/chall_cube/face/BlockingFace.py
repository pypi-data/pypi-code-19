from time import sleep
from .Face import Face


class BlockingFace(Face):

    def __init__(self, time=3):
        super().__init__()

        self.__time = time
        self.__has_stop_request = False

    def request_stop(self):
        self.__has_stop_request = True

    def start(self):
        self.print('Face running %d seconds...' % self.__time)

        for i in range(0, self.__time):
            sleep(1)

            if self.__has_stop_request:
                self.print('Stopped after stop request.')
                return

        self.print('End of %d seconds.' % self.__time)
