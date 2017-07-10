class Face:

    def __init__(self):
        self.__index = None

    def get_index(self):
        return self.__index

    def set_index(self, index):
        self.__index = index

        return self

    def get_name(self):
        return 'Face %d' % (self.__index + 1)

    def request_stop(self):
        pass

    def start(self):
        self.print('Face starting')

    def print(self, message):
        print('%s: %s' % (self.get_name(), message))
