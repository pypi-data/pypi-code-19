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
        self.config = config
        from .input_gpio import input_GPIO
        self.input = input_GPIO(self, config['gpiocont'])



    def input_event(self, event):
        logger.debug("GPIOcont: Input event arrived at frontend.")

        if event['main'] == 'play':
            if self.core.playback.state.get() == \
                    core.PlaybackState.PLAYING:
                self.core.playback.pause()
            else:
                self.core.playback.play()

        if event['main'] == 'volume':
            if event['sub'] == 'up':
                curr = self.core.playback.volume.get()
                self.core.playback.volume = curr+vol_change
                logger.debug("GPIOcont: volume up.")
            else:
                curr = self.core.playback.volume.get()
                self.core.playback.volume = curr - vol_change

        if event['main'] == 'list':
            logger.debug("GPIOcont: List in frontend.py detected.")
            if event['sub'] == 'list1':
                self.core.tracklist.clear()
                logger.debug("GPIOcont: cleared")

                for i in self.core.playlists.playlists.get():
                    logger.debug(i)

                logger.debug("GPIOcont: That was your list")

                self.core.playlist.get_items(self.config['gpiocont']['list1_name'])
                logger.debug("GPIOcont: get items worked")

                self.core.tracklist.add(uri=self.config['list1_name'])
                logger.debug("GPIOcont: tracklist added")
                core.playback.play()
                logger.debug("GPIOcont: playing")


