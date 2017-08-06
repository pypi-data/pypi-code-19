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
            GPIO.setup(pins['vol_a_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(pins['vol_b_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['vol_a_pin'], GPIO.BOTH, callback=self.volume, bouncetime=vol_deb_time)

            #Dedicated playlist pins
            GPIO.setup(pins['list1_pin'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(pins['list1_pin'], GPIO.FALLING, callback=self.list1, bouncetime=deb_time)

            logger.debug("GPIOcont: pin events added.")
        except RuntimeError:
            logger.error("GPIOcont: Not enough permission to open GPIO.")

    def play(self, channel):
        self.frontend.input_event({'main': 'play', 'sub': 'none'})

    def volume(self, channel):
        if GPIO.input(channel)==1: #it was a rising edge
            if GPIO.input(self.pins['vol_b_pin']) == 0: #clockwise movement
                self.frontend.input_event({'main': 'volume', 'sub': 'up'})
            else: #counterclockwise movemnt
                self.frontend.input_event({'main': 'volume', 'sub': 'down'})

        else: # it was a falling edge.
            if GPIO.input(self.pins['vol_b_pin']) == 1: #clockwise movement
                self.frontend.input_event({'main': 'volume', 'sub': 'up'})
            else: #counterclockwise movement
                self.frontend.input_event({'main': 'volume', 'sub': 'down'})

    def list1(self, channel):
        self.frontend.input_event({'main': 'list', 'sub': 'list1'})
