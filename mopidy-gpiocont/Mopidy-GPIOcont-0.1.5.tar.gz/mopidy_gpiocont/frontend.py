import pykka
import logging

from mopidy import core


logger = logging.getLogger(__name__)

class gpio_control(pykka.ThreadingActor, core.Corelistener):

    def __init__(self, config, core):
        super(gpio_control, self.__init__())
        from .input_gpio import input_GPIO
        self.input = input_GPIO(self, config['gpiocont'])
        logger.info("frontend setup done")

    def input(self, input_event):
        logger.info("gpio event")
        if input_event == 'play':
            if self.core.playback.state.get() == \
                    core.PlaybackState.PLAYING:
                self.core.playback.pause()
            else:
                self.core.playback.play()
