from time import sleep
from gpiocrust import Header, OutputPin
from .Face import Face


class BlinkingFace(Face):

    def __init__(self, pin_number, delay=0.5):
        super().__init__()

        self.__has_stop_request = False

        self.__pin_number = pin_number
        self.__delay = delay

    def request_stop(self):
        self.__has_stop_request = True

    def start(self):
        self.print('Blinking face start.')

        with Header():
            pin = OutputPin(self.__pin_number)

            while not self.__has_stop_request:
                pin.value = 1
                self.print('Blinking pin ON')
                sleep(self.__delay)
                pin.value = 0
                self.print('Blinking pin OFF')
                sleep(self.__delay)
