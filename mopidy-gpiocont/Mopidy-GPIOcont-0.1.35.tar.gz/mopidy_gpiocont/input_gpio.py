import RPi.GPIO as GPIO

import logging
logger = logging.getLogger(__name__)
logger.debug("GPIOcont: input_gpio.py called.")

class input_GPIO():
    def __init__(self, frontend, pins):
        self.frontend = frontend

        try:
            # set pin mode to BCM
            GPIO.setmode(GPIO.BCM)
            logger.debug("GPIOcont: Pinmode set.")
            # Play button
            GPIO.setup(pins['play_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['play_pin'], GPIO.FALLING, callback=self.play, bouncetime=30)

            logger.debug("GPIOcont: pin events added.")
        except RuntimeError:
            logger.error("GPIOcont: Not enough permission to open GPIO")

    def play(self, channel):
        logger.debug("GPIOcont: Play pin pressed.")
        self.frontend.input_event('play')
        if GPIO.input(channel)==0:
            logger.debug("GPIOcont: Button pressed input_g  pio.py.")