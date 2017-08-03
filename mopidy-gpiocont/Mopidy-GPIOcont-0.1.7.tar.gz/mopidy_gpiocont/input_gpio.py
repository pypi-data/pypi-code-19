import RPi.GPIO as GPIO

import logging
logger = logging.getLogger(__name__)

class input_GPIO():
    def __init__(self, frontend, pins):
        self.frontend = frontend

        try:

            # set pin mode to BCM
            GPIO.setmode(GPIO.BCM)

            # Play button
            GPIO.setup(pins['play_pin'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
            GPIO.add_event_detect(pins['play_pin'], GPIO.FALLING, callback=self.play, bouncetime=30)

        except RuntimeError:
            logger.error("TTSGPIO: Not enough permission ")

    def play(self, channel):
        self.frontend.input_event('play')
