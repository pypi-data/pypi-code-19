import pykka
import logging

from mopidy import core


logger = logging.getLogger(__name__)

class gpio_control(pykka.ThreadingActor, core.Corelistener):

    def __init__(self, config, core):
        super(gpio_control, self).__init__()
        self.core = core
        from .input_gpio import input_GPIO
        self.input = input_GPIO(self, config['gpiocont'])
        logger.info("frontend setup done")
        file2 = open("debug_frontend.txt", "w")
        file2.write(" frontend init")
        file2.close()

    def input(self, input_event):
        print "input dingen event jeweet"
        file2 = open("debug_frontend.txt", "w")
        file2.write("event!")
        file2.close()
        if input_event == 'play':
            if self.core.playback.state.get() == \
                    core.PlaybackState.PLAYING:
                self.core.playback.pause()
            else:
                self.core.playback.play()
