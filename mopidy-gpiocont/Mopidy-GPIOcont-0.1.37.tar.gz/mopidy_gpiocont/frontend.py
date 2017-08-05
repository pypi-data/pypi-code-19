import pykka
import logging

from mopidy import core

logger = logging.getLogger(__name__)
logger.debug("GPIOcont: Frontend.py called")

vol_change = 10

class GPIOcont(pykka.ThreadingActor, core.CoreListener):

    def __init__(self, config, core):
        super(GPIOcont, self).__init__()
        self.core = core
        from .input_gpio import input_GPIO
        self.input = input_GPIO(self, config['gpiocont'])



    def input_event(self, event):
        logger.error("GPIOcont: Input event arrived at frontend.")

        if event == 'play':
            if self.core.playback.state.get() == \
                    core.PlaybackState.PLAYING:
                self.core.playback.pause()
            else:
                self.core.playback.play()

        if event == 'vol_up':
            curr = self.core.playback.volume.get()
            self.core.playback.volume = curr+vol_change

        if event == 'vol_down':
            curr = self.core.playback.volume.get()
            self.core.playback.volume = curr-vol_change
