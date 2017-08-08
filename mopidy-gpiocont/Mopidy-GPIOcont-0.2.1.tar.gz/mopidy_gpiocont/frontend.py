import pykka
import logging
from time import sleep
logger = logging.getLogger(__name__)

from mopidy import core

try:
    import I2C_LCD_driver
except ImportError:
    logger.error("GPIOcont: could not import I2C bus.")



logger.debug("GPIOcont: Frontend.py called")

vol_change = 2 # Default volume change

class GPIOcont(pykka.ThreadingActor, core.CoreListener):

    def __init__(self, config, core):
        super(GPIOcont, self).__init__()
        self.core = core
        self.conf = config
        from .inout_gpio import inout_GPIO
        self.IO = inout_GPIO(self, config['gpiocont'])

        #Initialize the LCD display
        try:
            lcd_addr = int(config['gpiocont']['lcd_address'], 16) #Converts the address string (i.e. '0x38') to a hex integer
            lcd_port = config['gpiocont']['lcd_port']
            self.lcd = I2C_LCD_driver.lcd(lcd_addr, lcd_port)
            self.lcd.lcd_display_string("BOOTING", 1)
            self.lcd.lcd_display_string("git: jaspergerth", 2)
            sleep(0.5)
            self.lcd.lcd_clear()
        except IOError:
            logger.error("GPIOcont: Unable to initialize I2C bus, make sure mopidy is in i2c group <sudo adduser mopidy i2c>")

        #Set some tracklist attributes
        self.core.tracklist.set_repeat(True)

    def input_event(self, event):

        if event['main'] == 'play':
            logger.debug("play")
            if self.core.playback.state.get() == \
                    core.PlaybackState.PLAYING:
                self.core.playback.pause()
            else:
                self.core.playback.play()

        elif event['main'] == 'volume':
            if event['sub'] == 'up':
                curr = self.core.playback.volume.get()
                self.core.playback.volume = curr + self.conf['vol_change']
            else:
                curr = self.core.playback.volume.get()
                self.core.playback.volume = curr - self.conf['vol_change']

        elif event['main'] == 'list':
            toPlay = None
            self.core.tracklist.clear()
            for toPlay in self.core.playlists.playlists.get():
                if toPlay.name == event['sub']:
                    break
            for tr in toPlay.tracks:
                self.core.tracklist.add(uri=tr.uri)
            self.core.playback.play()

        elif event['main'] == 'switch':
            if event['sub'] == 'next':
                self.core.playback.next()
            elif event['sub'] == 'prev':
                self.core.playback.previous()


