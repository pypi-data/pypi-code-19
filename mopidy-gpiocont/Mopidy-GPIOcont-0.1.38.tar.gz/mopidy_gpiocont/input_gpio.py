import RPi.GPIO as GPIO

import logging
logger = logging.getLogger(__name__)
logger.debug("GPIOcont: input_gpio.py called.")

deb_time = 50 #The debounce time for the buttons
vol_deb_time = 50 # The debounce time for the rotary encoder

class input_GPIO():
    def __init__(self, frontend, pins):
        self.frontend = frontend
        self.pins = pins
        try:
            # set pin mode to BCM
            GPIO.setmode(GPIO.BCM)

            # Play button
            GPIO.setup(pins['play_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['play_pin'], GPIO.FALLING, callback=self.play, bouncetime=deb_time)

            #Volume rotary encoder
            GPIO.setup(pins['vol_A_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(pins['vol_B_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['vol_A_pin'], GPIO.BOTH, callback=self.volume, bouncetime=vol_deb_time)

            logger.debug("GPIOcont: pin events added.")
        except RuntimeError:
            logger.error("GPIOcont: Not enough permission to open GPIO")

    def play(self, channel):
        self.frontend.input_event('play')

    def volume(self,channel):
        logger.debug("Volume event.")
        if GPIO.input(channel)==1: #it was a rising edge
            if GPIO.input(self.pins['vol_B_pin']) == 0: #clockwise movement
                logger.debug ("Volume up!")
            else: #counterclockwise movemnt
                logger.debug("Volume down")

        else: # it was a falling edge.
            if GPIO.input(self.pins['vol_B_pin']) == 1: #clockwise movement
                logger.debug("volume up")
            else: #counterclockwise movement
                logger.debug("Volume down")