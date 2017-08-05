import RPi.GPIO as GPIO

import logging
logger = logging.getLogger(__name__)
logger.warning("GPIOcont: input gpio dingen")

class input_GPIO():
    def __init__(self, frontend, pins):
        self.frontend = frontend

        try:

            # set pin mode to BCM
            GPIO.setmode(GPIO.BCM)

            # Play button
            GPIO.setup(pins['play_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['play_pin'], GPIO.FALLING, callback=self.play, bouncetime=30)

        except RuntimeError:
            logger.error("GPIOcont: Not enough permission to open GPIO")

    def play(self, channel):
        self.frontend.input_event('play')
        logger.debug("GPIOcont: Play pin pressed.")
            if GPIO.input(channel)==0:
                logger.debug("GPIOcont: Button pressed input_gpio.y.")