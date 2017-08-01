import pykka
from modipy import core



class gpio_control(pykka.ThreadingActor, core.Corelistener):

    def __init__(self):
        super(gpio_control, self.__init__())
        from .input_gpio import input_GPIO
        self.input = input_GPIO(self, config['gpio_control'])

    def input(self, input_event):
        if input_event == 'play':
            print('hoer')
            print(self.core.playlists.playlists.get())
            vol = self.core.playback.volume.get()
            vol += 10
            self.core.playback.volume = vol